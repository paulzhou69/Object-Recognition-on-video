import os
import numpy as np
from darknet.darknet import performDetect
from observation_parser import parse_yolo_output
from iou.compute import compute_iou, compute_giou
from iou.increase_confidence import percent_increase, first_time_decrease
from iou.move_object import move_object
from imu.displacement import compute_displacement_pr
from imu.image_info import get_angle, get_distance_center
from config import *


# get the images from input
img_path_ls = []  # a list of image paths
for image in os.scandir(image_directory):
    if image.path.endswith('.jpg') or image.path.endswith('.png') and image.is_file():
        img_path_ls.append(image.path)
img_path_ls.sort()


# incorporate IMU and depth info
imu_ls = np.loadtxt(imu_directory, delimiter=',')

# assert len(img_path_ls) == len(imu_ls), "Length of IMU input should match length of camera input"


# process single result form darknet
def process_img(img_path: str) -> []:
    """
    input: a str, absolute path to the img
    output: a list of objs, [obj1, obj2, ....],
            where obj = [class1, class2, ... , class80]
            where class = ('tag', confidence, (x, y, w, h))
            The X and Y coordinates are from the center of the bounding box, w & h are width and height of the box
    """
    if not os.path.exists(img_path):
        raise ValueError("Invalid image path: " + img_path)
    detect_result: {} = performDetect(imagePath=img_path, thresh=0.10,
                                      metaPath="./darknet/cfg/kf_coco.data", showImage=saveImage)
    parsed_result: [] = parse_yolo_output(detect_result)
    return parsed_result


def get_max_con_class(full_distr: []) -> ():
    """
    get the class with greatest confidence in an object with full probability distribution \
    input: [class1, class2, ... , class80]
            where class = ('tag', confidence, (x, y, w, h))
    output: classN, the class with the greatest confidence
    """
    sorted_list = sorted(full_distr, key=lambda x: -x[1])
    return sorted_list[0]


# loop YOLO and iou
# the outputs shall all be of single distribution, as opposed to the darknet.py output
def update(giou: bool = True) -> ():
    """
    this is where the bulk of the computation happens, using IMU info and past recognition results to update the current
    recognition
    input: True if we use generalized IoU to update the result
           False if we use the regular IoU
    output: original_obser_ls: the recognition result outputed by YOLO
            updated_obser_ls: the recognition result after being updated with IMU info
            iou_ls: the list of top IOU for each obj
    """
    global current_obj_max_iou
    original_obser_ls = []
    updated_obser_ls = []
    iou_ls = []
    previous_objects: [] = []
    seen_objects: [] = []  # tags of objects already seen in the video sequence
    for i in range(len(img_path_ls)):

        # load info
        if debug: print("------start loop")
        img_path = img_path_ls[i]
        if debug: print("------got path: ", img_path)
        # angular_speed_ls = []  # all imu samples between two frames
        # for k in range(between_frame_count):
        #     angular_speed = imu_ls[i * between_frame_count + k]
        #     angular_speed_ls.append(angular_speed)
        # if debug: print("-------got angular speed list: ", angular_speed_ls)
        angular_speed = imu_ls[i]
        vx, vy, vz = angular_speed[0], angular_speed[1], angular_speed[2]
        if debug: print("------got angular speed: ", vx, vy, vz)
        objects: [] = process_img(img_path)
        if debug: print("------processed img: ", len(objects), "objects detected")

        # move objects in previous frame
        moved_objs = []  # the list for old objs after they've been moved to the new predicted location
        for prev_obj in previous_objects:
            if debug: print("--------previous object is :", prev_obj)
            # dx, dy = 0, 0  # initialize dx, dy
            # for av in angular_speed_ls:  # integrate the imu info between two frames to get the actual displacement
            #     vx, vy, vz = av[0], av[1], av[2]
            #     delta_dx, delta_dy = \
            #         compute_displacement_pr(vx, vy, vz, get_distance_center(prev_obj[2]), get_angle(prev_obj[2]))
            #     dx += delta_dx
            #     dy += delta_dy
            dx, dy = compute_displacement_pr(vx, vy, vz, get_distance_center(prev_obj[2]), get_angle(prev_obj[2]))
            moved_obj = move_object(prev_obj, dx, dy)
            if debug: print("--------moved previous obj to: ", moved_obj)
            moved_objs.append(moved_obj)

        # process current frame
        processed_objs = []  # the list for objs after confidence are increased
        unprocessed_objs = []  # the list for objs as YOLO detects them
        frame_ious = []  # the top iou for each object in current frame
        for current_obj in objects:
            max_con_class = get_max_con_class(current_obj)
            if debug: print("--------current most likely object: ", max_con_class)
            # if debug: print("--------current object with full distribution: ", current_obj)
            if get_original:
                unprocessed_objs.append(max_con_class)
                if debug: print("--------original object is", max_con_class)
            current_obj_ious = {}  # keys: class tags, values: iou score for that class, for the current object
            if max_con_class[0] not in seen_objects:  # if the object is not seen during previous part of the video
                first_time_decrease(current_obj, max_con_class[0], percent=0.2)
                seen_objects.append(max_con_class[0])
            for old_obj in moved_objs:
                iou_score = compute_giou(old_obj[2], current_obj[0][2])
                if not giou:
                    iou_score = compute_iou(old_obj[2], current_obj[0][2])
                if debug: print("------computed iou: ", iou_score)
                if get_iou:
                    if old_obj[0] in current_obj_ious:
                        current_obj_ious[old_obj[0]] = max(iou_score, current_obj_ious[old_obj[0]])
                    else:
                        current_obj_ious[old_obj[0]] = iou_score
                if iou_score >= iou_thresh:
                    percent_increase(current_obj, old_obj[0], percent=0.5)  # TODO: can change increase method here
            new_max_con_class = get_max_con_class(current_obj)
            processed_objs.append(new_max_con_class)
            if debug: print('------adding object: ', new_max_con_class)
            if get_iou:
                if new_max_con_class[0] in current_obj_ious:
                    max_con_class_iou = current_obj_ious[new_max_con_class[0]]
                else:
                    max_con_class_iou = 0
                frame_ious.append((new_max_con_class[0], max_con_class_iou))
                if debug: print('------adding iou ', new_max_con_class[0], max_con_class_iou)
        if debug: print("------increased all confidence possible")
        previous_objects = processed_objs
        if debug: print("------saved to previous objects")
        updated_obser_ls.append(processed_objs)
        if debug: print("------saved to processed objects")
        if get_original:
            original_obser_ls.append(unprocessed_objs)
            if debug: print("------added original unprocessed items")
        if get_iou:
            iou_ls.append(frame_ious)
            if debug: print("------added iou of the frame")
        if debug: print("------end loop")
    return original_obser_ls, updated_obser_ls, iou_ls

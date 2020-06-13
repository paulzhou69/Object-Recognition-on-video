from darknet.darknet import performDetect, performBatchDetect, detect_image, detect
from darknet.darknet_video import YOLO
from observation_parser import parse_yolo_batch_output, parse_yolo_output
from kf.kf_v1 import KF
from kf.object_dict import object_name_to_index
from kf.make_observation import observation_to_nparray_v4
import cv2


# process batch result from darknet
"""
the result is in the form of ([[batch_boxes]], [[batch_scores]], [[batch_classes]])
"""
# batch_detect_result = performBatchDetect(thresh=0.70,
#                                          configPath="./darknet/cfg/yolov3.cfg",
#                                          weightPath="darknet/yolov3.weights",
#                                          metaPath="./darknet/cfg/kf_coco.data",
#                                          batch_size=3,
#                                          input_images=['darknet/data/person.jpg', 'darknet/data/horses.jpg', 'darknet/data/dog.jpg'])
# parsed_batch_result: [] = parse_yolo_batch_output(batch_detect_result)
# batch_result_array = observation_to_nparray_v2(parsed_batch_result)  # convert the result to a numpy array TODO:


# process single result form darknet
"""
('obj_label', confidence, (bounding_box_x_px, bounding_box_y_px, bounding_box_width_px, bounding_box_height_px))
The X and Y coordinates are from the center of the bounding box. 
"""
detect_result: {} = performDetect(imagePath="darknet/data/horses.jpg", thresh=0.70,
                                  metaPath="./darknet/cfg/kf_coco.data", showImage=False)
parsed_result: [] = parse_yolo_output(detect_result)
indexed_result: [] = object_name_to_index(parsed_result)
result_array, unprocessed_objects = observation_to_nparray_v4(indexed_result)  # convert the result to a numpy array


# process result of darknet from detect_image, this gives the full probability distribution
# image = cv2.imread("darknet/data/person.jpg")
# detect_result = detect(net="./darknet/cfg/yolov3.cfg", meta="./darknet/cfg/kf_coco.data", image=image, thresh=.5,
#                        hier_thresh=.5, nms=.45)

# incorporate IMU and depth info
# TODO: need more info

# apply the Kalman Filter

# see the results
if __name__ == "__main__":
    print("------------------------------------")
    print(parsed_result)
    print(indexed_result)
    print(result_array)
    print(unprocessed_objects)
    print("------------------------------------")

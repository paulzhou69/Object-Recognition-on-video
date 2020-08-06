# this file holds all the variables that need to be changed before using the object recognition-IMU API

# debugger
debug = True  # set this to true to print informative messages


# detection
detection_thresh = 0.4
moved_iou_thresh = 0.4
N = 4
decay_rate = 0.5
delta_score = 0.2
OBJ_NAME = 'car'
TEST_NAME = OBJ_NAME + '3'
test_thresh = 0.5
frame_num_dict = {
    'boat': 89,
    'bird': 71,
    'person': 194,
    'dog': 660,
    'cat': 85,
    'zebra': 121,
    'car': 93,
    'car2': 81,
    'car3': 152,
    'motorbike': 96,
    'aeroplane': 1419,
    'bear': 287,
    'sheep': 102,
    'bear2': 78,
    'boat2': 43
}
NUM_FRAME = frame_num_dict[TEST_NAME]


# compare results
get_original = True
saveImage = False  # save the image with bounding boxes


# paths
ground_truth_directory = "./input/ground_truth/" + TEST_NAME
image_directory = "./input/image/" + TEST_NAME  # input images, used in kf_update.py & iou_update.py
quaternion_path = 'imu/quaternion.csv'
gyro_path = 'imu/gyro_data.csv'
acc_path = 'imu/acc_data.csv'
imu_time_path = 'imu/imu_time.csv'
img_time_path = 'imu/img_time.csv'
raw_imu_path = 'input/imu/imu_recordings.csv'  # the path to the imu data file, used in imu/raw_data.py
raw_timestamp_path = 'input/imu/img_timestamp.csv'  # the path to the timestamp data file, used in imu/raw_data.py
iou_output_path = './iou_output/'  # the directory of outputs of IOU, used in iou_update.py
kf_output_path = './kf_output/'  # the directory of outputs of KF, used in kf_update.py


# camera info
default_depth = 3  # the distance between the camera and the object seen, in meters
fps = 30  # frame rate of camera
dt = 1 / fps
width_angle = 159  # in degrees, the width angle of view from the RGB camera
height_angle = 127  # in degrees, the height angle of view from the RGB camera
focus = 0.01  # the distance between the camera eye and the screen where picture is formed. in meters


# image info
pixel_width = 1280  # the length of a single picture, in pixel units
pixel_height = 720  # the height of a single picture, in pixel units


# imu info
imu_rate = 38.5  # the sampling rate of the imu


# raw data bias
abias_x, abias_y, abias_z = 0.0, 0.0, 0.0  # accelerometer bias
gbias_x, gbias_y, gbias_z = -0.0, -0.0, -0.0  # gyroscope bias
rot_x, rot_y, rot_z = -0.0, 0.0, -0.0  # axis-angle vector of
# IMU-to-camera rotation
time_offset = 0  # time offset between the camera and the imu


# kf
increase_confidence = True  # set to true if you want the underlying Kalman Filter to increase the confidence of
# objects at every "predicting" stage, while moving the objects to a new location according to the IMU input
# the indices in the Kalman Filter state vector
num_max = 2  # the number of maximum objects assumed to be detected in each frame
num_obj = 80  # the total number of classes of objects that can be recognized by the recognition alg
iC = 0  # relative index of c, the confidence score of the object recognized, taking value in [0, 1]
iX = 1  # relative index of x, the x-position of the center of the bounding box
iY = 2  # relative index of y, the y-position of the center of the bounding box
iW = 3  # relative index of w, the width of the bounding box
iH = 4  # relative index of h, the height of the bounding box
num_var = iH + 1
dim = num_max * num_obj * num_var  # the dimension of the state vector


# iou
giou_thresh = 0.55  # generalized iou score threshold for increasing confidence
iou_thresh = 0.6  # iou score threshold for increasing confidence
get_iou = True

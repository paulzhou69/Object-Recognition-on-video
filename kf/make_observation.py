import numpy as np
from pyquaternion import Quaternion
from kf.kf_v1 import TOTOALNUM, NUMVARS
from kf.kf_v4 import input_dim
from object_dict import index_to_object
from imu.image_info import get_angle, get_distance_center
from imu.displacement import compute_displacement_pr, compute_displacement_quaternion
from config import *


def observation_to_nparray_v1(observ: []) -> np.array:
    """
    this method is for kf_v1
    """
    # observ is a list of recognized object, which are lists themselves
    final_array = np.zeros((TOTOALNUM, 1))
    for recognized_objects in observ:
        object_index = recognized_objects[0]
        start_index = object_index * NUMVARS
        final_array[start_index] = recognized_objects[1]
        final_array[start_index + 1] = recognized_objects[2]
        final_array[start_index + 2] = recognized_objects[3]
        final_array[start_index + 3] = recognized_objects[4]
        final_array[start_index + 4] = recognized_objects[5]
    return final_array


def observation_to_nparray_v4(observ: []) -> (np.array, []):
    """
    this method is for kf_v4
    input: [obj1, obj2, obj3, ...], where obj is (tag: int, con, (x, y, w, h))
    output1: np.array of shape (dim, 1)
            [[obj1 occurrence 1],
             [obj1 occurrence 2],
             ...
             [obj1 occurrence num_max],
             [obj2 occurrence 1],
             ... ]
    output2: a list of unprocessed objects: [obj1, obj2, ...], where obj is (tag: int, con, (x, y, w, h))
    """
    visited = {}  # keys: indices (objects) already encountered;  values: the number of times encountered
    unprocessed = []
    final_array = np.zeros((dim, 1))
    for object in observ:
        index = object[0]

        if index in visited and visited[index] >= num_max:
            unprocessed.append(object)
        else:
            if index in visited:
                visited[index] += 1
            if index not in visited:
                visited[index] = 1
            current_occurrence = visited[index]
            start_index = index * num_max * num_var + num_var * (current_occurrence - 1)
            final_array[start_index] = object[1]  # con
            final_array[start_index + 1] = object[2][0]  # x
            final_array[start_index + 2] = object[2][1]  # y
            final_array[start_index + 3] = object[2][2]  # w
            final_array[start_index + 4] = object[2][3]  # h
    return final_array, unprocessed


def nparray_to_observation_v4(arr: np.array, unprocessed: []) -> []:
    """
    this method is for kf_v4
    input1: np.array of shape (dim, 1), the output1 of function observation_to_nparray_v4
    input2: a list of unprocessed objs, where obj is (tag: int, con, (x, y, w, h))
    output: a list of obj observations, concat input1.toList and input2, where obj is (tag: str, con, (x, y, w, h))
    """
    obj_ls = []
    for object_index in range(num_obj):
        for occurrence_index in range(num_max):
            start_index = occurrence_index * num_var + object_index * num_var * num_max
            if arr[start_index][0] != 0:  # confidence of obj is not 0
                tag: str = index_to_object[object_index]
                obj = (tag, arr[start_index][0], (arr[start_index + 1][0], arr[start_index + 2][0], arr[start_index + 3][0], arr[start_index + 4][0]))
                obj_ls.append(obj)
    return obj_ls + unprocessed


def make_u(arr: np.array, vx: float, vy: float, vz: float) -> np.array:
    """
    input: using the current state array arr and three angular velocities vx, vy, vz
    output: the control-input u
    """
    u = np.zeros((input_dim, 1))
    pointer = 0
    for i in range(num_max * num_obj):
        start_index = i * num_var
        if arr[start_index] != 0:
            end_index = start_index + num_var
            box: np.array = arr[start_index + iX: end_index]
            box: () = tuple(box)  # convert the np.array to tuple
            dx, dy = compute_displacement_pr(vx, vy, vz, get_distance_center(box), get_angle(box), delta_t=(1 / imu_rate))
            u[pointer], u[pointer + 1] = dx, dy
        pointer += 2
    return u


def make_u_quaternion(arr: np.array, delta_q: Quaternion) -> np.array:
    """
    input: using the current state array arr and three angular velocities vx, vy, vz
    output: the control-input u
    """
    u = np.zeros((input_dim, 1))
    pointer = 0
    for i in range(num_max * num_obj):
        start_index = i * num_var
        if arr[start_index] != 0:
            dx, dy = compute_displacement_quaternion(delta_q)
            u[pointer], u[pointer + 1] = dx, dy
        pointer += 2
    return u

import numpy as np
from utils import DLT, get_projection_matrix, write_keypoints_to_disk
import collections
import pickle

def extract_2d_pose_for_a_subject(input_stream, num_classes, frame_number, monkey_name):
    pose_camera = None
    for j in range(num_classes):
        if len(input_stream) > j:
            if int(input_stream[j][0]) == (frame_number + 1):
                if str(input_stream[j][1]) == monkey_name:
                    pose_camera = input_stream.pop(j)
                    break
            else:
                break
        else:
            break
    return pose_camera

def check_confidence_pose(uv, conf_thresh):
    uvs = []
    for id, x in enumerate(uv):
        if (id % 3 == 0):
            if uv[id + 2] > conf_thresh:
                uvs.append(x)
            else:
                uvs.append(-1)
        if (id % 3 == 1):
            if uv[id + 1] > conf_thresh:
                uvs.append(x)
            else:
                uvs.append(-1)
    return uvs

def run_3d(input_stream1, input_stream2, P0, P1, transformation, coordinate_system_xyz, coordinate_system_flip, classes, num_frames, conf_thresh):

    camera_primary_to_corner_of_room_x = coordinate_system_xyz[0]
    camera_primary_to_corner_of_room_y = coordinate_system_xyz[1]
    camera_primary_to_corner_of_room_z = coordinate_system_xyz[2]

    transformation_matrix = transformation

    flip_x = coordinate_system_flip[0]
    flip_y = coordinate_system_flip[1]
    flip_z = coordinate_system_flip[2]

    kpts_3d = [[] for _ in range(len(classes))]
    num_classes = len(classes)

    for i in range(num_frames):
        for idk, k in enumerate(classes):
            # in results txt file related to each camera, extract pose for frame i, for each monkey separately
            # first camera
            pose_camera1 = extract_2d_pose_for_a_subject(input_stream1, num_classes, i, k)
            # second camera
            pose_camera2 = extract_2d_pose_for_a_subject(input_stream2, num_classes, i, k)

            if (pose_camera1 is not None) and (pose_camera2 is not None):
                p3ds = []
                uv1 = pose_camera1[7:] # extract keypoints
                uv2 = pose_camera2[7:] # extract keypoints
                uv1 = [float(x) for x in uv1]
                uv2 = [float(x) for x in uv2]
                uvs1 = check_confidence_pose(uv1, conf_thresh) # check confidence for each keypoint + remove confidence values
                uvs2 = check_confidence_pose(uv2, conf_thresh) # check confidence for each keypoint + remove confidence values
                uvs1 = zip(uvs1[::2], uvs1[1::2]) # transform list to [(x1, y1), ...] format
                uvs2 = zip(uvs2[::2], uvs2[1::2]) # transform list to [(x1, y1), ...] format

                for uv1, uv2 in zip(uvs1, uvs2):
                    if uv1[0] == -1 or uv2[0] == -1: # no keypoint captured
                        _p3d = [-1, -1, -1]
                    else:
                        _p3d = DLT(P0, P1, uv1, uv2)
                        _p3d = transformation_matrix @ _p3d
                        _p3d[0] = flip_x * (_p3d[0]) + camera_primary_to_corner_of_room_x
                        _p3d[1] = flip_y * (_p3d[1]) + camera_primary_to_corner_of_room_y
                        _p3d[2] = flip_z * _p3d[2] + camera_primary_to_corner_of_room_z
                    p3ds.append(_p3d)
                p3ds = np.array(p3ds)
                kpts_3d[idk].append(p3ds)
            else:
                p3ds = []
                for ii in range(17):
                    _p3d = [-1, -1, -1]
                    p3ds.append(_p3d)
                p3ds = np.array(p3ds)
                kpts_3d[idk].append(p3ds)

    for i in range(len(kpts_3d)):
        print('len(kpts_3d): ', len(kpts_3d[i]))

    return kpts_3d

if __name__ == '__main__':

    num_frames = 19635 # fps * seconds

    input_stream1 = './2d_results_txt/Camera_0_keypoint.txt'
    input_stream2 = './2d_results_txt/Camera_4_keypoint.txt'
    # input_stream1 = './results_txt/Camera_0_keypoint.txt'
    # input_stream2 = './results_txt/Camera_4_keypoint.txt'

    with open(input_stream1) as file:
        input_stream1_lines = [line.rstrip() for line in file]
    with open(input_stream2) as file:
        input_stream2_lines = [line.rstrip() for line in file]
    input_stream1_lines.pop(0)
    input_stream2_lines.pop(0)
    for i in range(len(input_stream1_lines)):
        input_stream1_lines[i] = input_stream1_lines[i].split(' ')
    for i in range(len(input_stream2_lines)):
        input_stream2_lines[i] = input_stream2_lines[i].split(' ')

    # # get projection matrices
    # P0 = get_projection_matrix(2)
    # P1 = get_projection_matrix(3)

    # # matching the room coordinate system
    # # camera 2, camera 3
    # # transform matrix to rotate coordinate system
    # transformation = np.array([[1.13152077,  0.67168103, - 0.24667943],
    #                         [-0.04553358,  0.81800656,  0.44962481],
    #                         [0.51467712, - 1.50746732, 0.86808287]])

    # # translate coordinate system to match room coordinate system origin
    # camera_primary_x = 300 # in millimeter, related to coordinate system origin
    # camera_primary_y = 1200 # in millimeter, related to coordinate system origin
    # camera_primary_z = 0 # in millimeter, related to coordinate system origin
    # # flip coordinate system to match room coordinate system
    # flip_x = -1  # camera 2 3
    # flip_y = -1  # camera 2 3
    # flip_z = 1  # camera 2 3

    # camera 0, camera 4
    # transformation = np.array([[0.98622111, - 0.13644845, 0.35622341],
    #                                  [0.01577515, 0.8494871, 0.47517198],
    #                                  [-0.41382915, - 0.6049505, 0.81043218]])
    # camera_primary_x = 200
    # camera_primary_y = -1200
    # camera_primary_z = -4500
    # flip_x = 1  # camera 0 4
    # flip_y = -1  # camera 0 4
    # flip_z = -1  # camera 0 4


    with open("calib_0_4.pickle", 'rb') as f:
        calibration_data = pickle.load(f)

    # coordinate_system_translate = [camera_primary_x, camera_primary_y, camera_primary_z]
    # coordinate_system_flip = [flip_x, flip_y, flip_z]

    classes = ['Vin', 'Nathan'] # monkeys
    conf_thresh = 0.1

    kpts_3d = run_3d(input_stream1_lines, input_stream2_lines, calibration_data["primary_mat"], calibration_data["secondary_mat"], calibration_data["transformation_mat"], [np.abs(x) for x in calibration_data["primary_cam"]['world_pos']], calibration_data["primary_cam"]['flip'], classes, num_frames, conf_thresh)
    for idz, i in enumerate(classes):
        write_keypoints_to_disk('./3d_results_txt_new/Camera_0_4_kpts_3d_' + i + '.txt', kpts_3d[idz])

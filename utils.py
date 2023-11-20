import numpy as np
from scipy import linalg
import yaml

# Define a function to remove or replace unsupported custom tags
def preprocess_yaml(file_path):
    with open(file_path, 'r') as file:
        # Skip the first line ("%YAML:1.0")
        file.readline()
        lines = file.readlines()
    # Remove or replace unsupported custom tags in the lines
    processed_lines = [line.replace('!!opencv-matrix', '') for line in lines]
    # Join the processed lines back into a string
    processed_yaml = ''.join(processed_lines)
    return processed_yaml

def DLT(P1, P2, point1, point2):
    A = [point1[1] * P1[2, :] - P1[1, :],
         P1[0, :] - point1[0] * P1[2, :],
         point2[1] * P2[2, :] - P2[1, :],
         P2[0, :] - point2[0] * P2[2, :]
         ]
    A = np.array(A).reshape((4, 4))
    # print('A: ')
    # print(A)

    B = A.transpose() @ A
    U, s, Vh = linalg.svd(B, full_matrices=False)

    # print('Triangulated point: ')
    # print(Vh[3, 0:3] / Vh[3, 3])
    return Vh[3, 0:3] / Vh[3, 3]

# def read_camera_parameters(camera_id):
#
#     mtx = np.loadtxt('camera_parameters/mtx'+ str(camera_id) + '.txt')  # 'mtx1.txt'
#     print('mtx:', mtx)
#     return mtx

def read_camera_parameters(camera_id):
    # Preprocess the YAML file to remove or replace unsupported custom tags
    # processed_yaml = preprocess_yaml('camera_parameters/Camera_'+ str(camera_id) + '.yaml')
    processed_yaml = preprocess_yaml(camera_id)
    # Load the preprocessed YAML data
    yaml_data = yaml.safe_load(processed_yaml)
    # Extract the data from the YAML structure
    intrinsic_matrix = yaml_data['intrinsicMatrix']['data']
    # Convert the extracted data into a 3x3 matrix
    intrinsic_matrix = [
        intrinsic_matrix[0:3],
        intrinsic_matrix[3:6],
        intrinsic_matrix[6:9]
    ]
    # Transpose the matrix
    intrinsic_matrix = list(map(list, zip(*intrinsic_matrix)))

    # Extract the data from the YAML structure for R and T matrices
    R_matrix = yaml_data['R']['data']
    R_matrix = [
        R_matrix[0:3],
        R_matrix[3:6],
        R_matrix[6:9]
    ]
    R_matrix = list(map(list, zip(*R_matrix)))

    T_matrix = yaml_data['T']['data']
    T_matrix = [
        [T_matrix[0]],
        [T_matrix[1]],
        [T_matrix[2]]
    ]

    # print('mtx:', intrinsic_matrix)
    # print('R:', R_matrix)
    # print('T:', T_matrix)
    return intrinsic_matrix, R_matrix, T_matrix

# def read_rotation_translation(camera_id):
#
#     R = np.loadtxt('camera_parameters/R'+ str(camera_id) + '.txt')  # 'R.txt'
#     T = np.loadtxt('camera_parameters/T'+ str(camera_id) + '.txt').reshape(3, 1)  # 'T.txt'
#     print('R:', R)
#     print('T:', T)
#     return R, T


def get_projection_matrix(camera_id):

    #read camera parameters
    cmtx, R, T = read_camera_parameters(camera_id)
    # R, T = read_rotation_translation(camera_id)

    RT = np.concatenate([R, T], axis=-1)
    P = cmtx @ RT  # projection matrix

    return P

def write_keypoints_to_disk(filename, kpts):
    fout = open(filename, 'w')

    for frame_kpts in kpts:
        # print(frame_kpts)
        for kpt in frame_kpts:

            if len(kpt) == 1:
                fout.write(str(kpt[0]) + ' ')
            elif len(kpt) == 2:
                fout.write(str(kpt[0]) + ' ' + str(kpt[1]) + ' ')
            elif len(kpt) == 3:
                fout.write(str(kpt[0]) + ' ' + str(kpt[1]) + ' ' + str(kpt[2]) + ' ')

        fout.write('\n')
    fout.close()


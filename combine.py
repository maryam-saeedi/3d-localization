import numpy as np

monkey = 'Vin' # 'Nathan' or 'Vin'
fps = 50
empty_text = ['-1']*(17*3)
input_3d_1 = './3d_results_txt_new/Camera_2_3_kpts_3d_'+monkey+'.txt' #  Camera_2_3_kpts_3d_Nathan.txt
input_3d_2 = './3d_results_txt_new/Camera_0_4_kpts_3d_'+monkey+'.txt' #  Camera_0_4_kpts_3d_Nathan.txt
f = open('./3d_results_txt_new/Cam_2_3_0_4_kpts_3d_'+monkey+'.txt',"w")

def read_lines(file_name):
    with open(file_name) as file:
        input_lines = [line.rstrip() for line in file]
    for i in range(len(input_lines)):
        input_lines[i] = input_lines[i].split(' ')
    return input_lines

input_3d_1_lines = read_lines(input_3d_1)
input_3d_2_lines = read_lines(input_3d_2)
print(input_3d_1_lines[0])
print(input_3d_2_lines[0])

def combine(keypoints, monkeys):
    for i in range(len(keypoints[0][0])):
        res = {}
        for idx, monkey in enumerate(monkeys):
            valid_points = [(j,len(np.where(keypoint[idx][i]!=-1.0)[0])) for j, keypoint in enumerate(keypoints)]
            valid_points = sorted(valid_points, key=lambda x: x[1], reverse=True)

            final_row = []
            if valid_points[0][1] == 17:
                final_row = keypoints[valid_points[0][0]][idx][i]
            else:
                for k, pnt in enumerate(keypoints[valid_points[0][0]][idx][i]):
                    if pnt[0] == '-1.0':
                        final_row.extend(np.mean([keypoint[idx][i][k] for keypoint in keypoints]))
                    else:
                        final_row.extend(pnt)
            res[monkey]=final_row
        yield res


for i in range(100):
    final_row = []
    final_txt = ''
    if input_3d_1_lines[i] == empty_text and input_3d_2_lines[i] == empty_text:
        final_row = empty_text
    elif input_3d_1_lines[i] != empty_text and input_3d_2_lines[i] == empty_text:
        final_row = input_3d_1_lines[i]
    elif input_3d_1_lines[i] == empty_text and input_3d_2_lines[i] != empty_text:
        final_row = input_3d_2_lines[i]
    else:
        final_row = []
        for j in range(0, len(input_3d_1_lines[i]), 3):
            if input_3d_1_lines[i][j] == '-1.0' and input_3d_2_lines[i][j] == '-1.0':
                final_row.extend([-1]*3)
            elif input_3d_1_lines[i][j] == '-1.0':
                final_row.extend(input_3d_2_lines[i][j:j+3])
            elif input_3d_2_lines[i][j] == '-1.0':
                final_row.extend(input_3d_1_lines[i][j:j+3])
            else:
                final_row.append((float(input_3d_1_lines[i][j])+float(input_3d_2_lines[i][j]))/2)
                final_row.append((float(input_3d_1_lines[i][j+1])+float(input_3d_2_lines[i][j+1]))/2)
                final_row.append((float(input_3d_1_lines[i][j+2])+float(input_3d_2_lines[i][j+2]))/2)

    for i17 in range(len(final_row)):
        final_txt += (str(final_row[i17]) + ' ')
    final_txt += '\n'

    f.write(final_txt)

f.close()
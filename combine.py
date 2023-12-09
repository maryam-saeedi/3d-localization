import numpy as np
from merge_regression import merge

def combine(keypoints, monkeys):
    for i in range(len(keypoints[0][0])):
        res = {}
        for idx, monkey in enumerate(monkeys):
            if len(keypoints) < 2:
                res[monkey] = keypoints[0][idx][i]
                continue

            valid_points = [(j,len(np.where(keypoint[idx][i]!=-1.0)[0])/3) for j, keypoint in enumerate(keypoints)]
            valid_points = sorted(valid_points, key=lambda x: x[1], reverse=True)

            final_row = []
            if valid_points[0][1] == 17 and valid_points[1][1] == 17:
                final_row.extend(np.mean([keypoint[idx][i] for keypoint in keypoints], axis=0))
            elif valid_points[0][1] == 0 or valid_points[1][1] == 0:
                if valid_points[0][1] != 0 :
                    final_row = keypoints[valid_points[0][0]][idx][i]
                else:
                    final_row = keypoints[valid_points[1][0]][idx][i]
                # final_row = [[-1.,-1.,-1.]]*17
            else:
                kp1, kp2 = merge(keypoints[valid_points[0][0]][idx][i], keypoints[valid_points[1][0]][idx][i])
                final_row.extend(np.mean([kp1, kp2], axis=0))

            # if valid_points[0][1] == 17:
            #     final_row = keypoints[valid_points[0][0]][idx][i]
            # else:
            #     for k, pnt in enumerate(keypoints[valid_points[0][0]][idx][i]):
            #         if pnt[0] == '-1.0':
            #             final_row.extend(np.mean([keypoint[idx][i][k] for keypoint in keypoints]))
            #         else:
            #             final_row.extend(pnt)
            res[monkey]=final_row
        yield res

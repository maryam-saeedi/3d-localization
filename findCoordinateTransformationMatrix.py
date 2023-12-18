import numpy as np
from utils import DLT, get_projection_matrix
import sys

def multiDimenDist(point1,point2):
    #find the difference between the two points, its really the same as below
    deltaVals = [point2[dimension]-point1[dimension] for dimension in range(len(point1))]
    runningSquared = 0
    #because the pythagarom theorm works for any dimension we can just use that
    for coOrd in deltaVals:
        runningSquared += coOrd**2
    return runningSquared**(1/2)

def findVec(point1,point2,unitSphere = False):
    #setting unitSphere to True will make the vector scaled down to a sphere with a radius one, instead of it's orginal length
    finalVector = [0 for coOrd in point1]
    for dimension, coOrd in enumerate(point1):
        #finding total differnce for that co-ordinate(x,y,z...)
        deltaCoOrd = point2[dimension]-coOrd
        #adding total difference
        finalVector[dimension] = deltaCoOrd
    if unitSphere:
        totalDist = multiDimenDist(point1,point2)
        unitVector =[]
        for dimen in finalVector:
            unitVector.append( dimen/totalDist)
        return unitVector
    else:
        return finalVector


# 3 points approach for finding transformation matrix
def find_transformation_matrix( P0, P1, three_points1, three_points2, three_points_real):

    # get projection matrices
    # P0 = get_projection_matrix(prinmary_cam) # camera 2
    # P1 = get_projection_matrix(secondary_cam) # camera 3
    # P0 = get_projection_matrix(0) # camera 0
    # P1 = get_projection_matrix(4) # camera 4

    p3ds = []
    for uv1, uv2 in zip(three_points1, three_points2):
        _p3d = DLT(P0, P1, uv1, uv2)
        p3ds.append(_p3d)

    vector1 = findVec(p3ds[0], p3ds[1])
    vector2 = findVec(p3ds[0], p3ds[2])
    crosspro = np.cross(vector1, vector2) # cross product must be non-zero vector to: 3 points be non-colinear points and matrix inveritrable
    crosspro_magnitude = np.linalg.norm(crosspro) # Calculate the magnitude of the cross product
    tolerance = 1e-6  # Define a tolerance value (small positive number)
    if crosspro_magnitude > tolerance:
        print("The cross product is a non-zero vector.")
    else:
        print("The cross product is a zero vector! 3 points must be non-colinear points.")
        sys.exit()


    system1 = np.array(p3ds).T
    system1_inv = np.linalg.pinv(system1) # Calculating the inverse of the matrix
    system2 = np.array(three_points_real).T
    transformation_matrix = system2 @ system1_inv
    print('transformation_matrix: ', transformation_matrix)
    # print(np.dot(transformation_matrix, p3ds[0]))

    return transformation_matrix


# 3 points 2d values
three_points1 = [(500, 330), (922, 386), (570, 386)] # camera 2
three_points2 = [(277, 388), (714, 347), (470, 419)] # camera 3
# same 3 points in 3d in Real world points (in new coordinate system)
three_points_real = [[-2500, 1200, 4500], [200, 1200, 4500], [-1600, 1200, 3600]] # camera 2 3

# three_points1 = [(296, 380), (725, 328), (487, 405)] # camera 0
# three_points2 = [(446, 336), (869, 355), (523, 386)] # camera 4
# three_points_real = [[-1774.31931839,  -813.77509712 , 4039.13044732], [  593.39959236, -1321.87548665,  4868.87974626], [-687.91914429, -608.69848379, 3636.43822415]] # camera 0 4

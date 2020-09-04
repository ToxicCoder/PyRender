import numpy as np
from math import *

# Material format
# [] - Container
# [[float, float, float]] - Red, Green and Blue vector
# [[float, float, float], float] - Previous + a specular control

# Material lists
matList0 = [
    [[1., 1., 1.], 1.],
    [[1., 0., 0.], 1.],
    [[0., 1., 0.], 1.],
    [[0., 0., 1.], 1.]]

matList1 = [
    [[1., 1., 1.], 0.],
    [[1., 0., 0.], 0.],
    [[0., 1., 0.], 0.],
    [[0., 0., 1.], 0.]]

# Materials
def assign(index, indexList):
    if type(indexList) == list:
        return indexList[index]
    elif type(indexList) == int:
        if indexList == 0:
            return matList0[index]
        elif indexList == 1:
            return matList1[index]
    else:
        raise ValueError(f"Invalid material index type {type(indexList)} expected list or int")

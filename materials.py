import numpy as np
from math import *

# Material format
# [[Red, Green, Blue], Specular, Emission]
# [[float, float, float], float, float]

# Material lists
matList0 = [
    [[1., 1., 1.], 1., 0.],
    [[1., 0., 0.], 1., 0.],
    [[0., 1., 0.], 1., 0.],
    [[0., 0., 1.], 1., 0.]]

matList1 = [
    [[1., 1., 1.], 0., 0.],
    [[1., 0., 0.], 0., 0.],
    [[0., 1., 0.], 0., 0.],
    [[0., 0., 1.], 0., 0.]]

matList2 = [ # Testing object lights
    [[1., 1., 1.], 0., 0.],
    [[1., 0., 0.], 0., 0.],
    [[1., 1., 1.], 0., 2.]]

# Materials
def assign(index, indexList):
    if type(indexList) == list:
        return indexList[index]
    elif type(indexList) == int:
        if indexList == 0:
            return matList0[index]
        elif indexList == 1:
            return matList1[index]
        elif indexList == 2:
            return matList2[index]
    else:
        raise ValueError(f"Invalid material index type {type(indexList)} expected list or int")

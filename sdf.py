import numpy as np
# Custom imports
from modifiers import *
from helpers import *

def sdSphere(point, location, radius, materialID=0, normal=False):
    return [length(location, point) - radius, materialID, normal]

def sdPlane(point, height=0, materialID=0, axis="z", normal=False):
    if "x" in axis.lower():
        dist = length(point, [height, point[1], point[2]])
    elif "y" in axis.lower():
        dist = length(point, [point[0], height, point[2]])
    elif "z" in axis.lower():
        dist = length(point, [point[0], point[1], height])
    else:
        raise ValueError("Axis must be either x, y or z")
    return [dist, materialID, normal]

def sdCube(point, b, materialID=0, normal=False):
    q = np.array([abs(x)-b for x in point])
    return [np.array(length([max(x, 0.0) for x in q])) + np.array(min(max(q[0], max(q[1], q[2])), 0.0)), materialID, normal]

def sdTorus(point, location, t, materialID=0, normal=False):
    point = np.array(point)-np.array(location)
    q = (length([point[0], point[1], 0], [0, 0, 0])-t[0], point[2], 0)
    return [length([q[0], q[1], q[2]], [0, 0, 0])-t[1], materialID, normal]

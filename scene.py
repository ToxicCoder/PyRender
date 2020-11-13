import numpy as np
from math import *

# Import custom modules
from sdf import *
from helpers import *
from modifiers import *
from materials import *

# Bundle Function
def bundleScene(unBundled, materialList, outputMode):
    if outputMode == 0:
        return unBundled[0]
    elif outputMode == 1:
        return assign(unBundled[1], materialList)
    elif outputMode == 2:
        return unBundled[2]
# Unbundled format is
# [distance, material, flip normal?]

# Define scene
def scene1(point, outputMode=0):
    materialList = 0 # Material indices
    # Objects
    plane = sdPlane(point, 0, 0)
    sphere = sdSphere(point, [0, 0, 1], 1, 1)#sdf_sphere([point[0], point[1], wrap(point[2], 2)], [0, 0, 1], 1, 1)
    output = opU(plane, sphere)
    # Output
    return bundleScene(output, materialList, outputMode)

def cornellBoxV1(point, outputMode=0):
    materialList = 0
    # Objects

    # Walls
    floor = sdPlane(point, 0, 0, axis="z", normal=True)
    ceiling = sdPlane(point, 6, 0, axis="z", normal=True)

    leftWall = sdPlane(point, -3, 1, axis="x")
    rightWall = sdPlane(point, 3, 2, axis="x", normal=True)

    backWall = sdPlane(point, -3, 0, axis="y", normal=True)

    output = opU(floor, ceiling) # Combine floor and ceiling
    output = opU(opU(leftWall, rightWall), output) # Add left and right walls
    output = opU(backWall, output) # Add back wall

    # Objects Inside
    #cube1 = sdCube(opT(point, [0, 0, 1]), 1, 2, normal=False)
    sphere1 = sdSphere(point, [0, 0, 1.5], 1, 0)

    #output = opU(cube1, output) # Add cube 1
    output = opU(sphere1, output) # Add sphere 1
    # Output
    return bundleScene(output, materialList, outputMode)

def cornellBoxV2(point, outputMode=0):
    materialList = 0 # Material indices
    # Walls
    ground = sdPlane(point, 0, 0)
    leftWall = sdPlane(point, -2, 0, axis="x", normal=False)

    # Objects
    sphere = sdSphere(point, [0, 0, 1], 1, 1)
    
    # Combine output
    output = opU(ground, leftWall)
    output = opU(output, sphere)
    # Output
    return bundleScene(output, materialList, outputMode)

def objectLightingTest(point, outputMode=0):
    materialList = 2 # Material indices
    # Walls
    ground = sdPlane(point, 0, 0)

    # Objects
    sphere = sdSphere(point, [0, 0, 1], 1, 1)
    #light = sdSphere(point, [0, 0, 4], 1, 2)
    
    # Combine output
    output = opU(ground, sphere)
    #output = opU(output, light)
    # Output
    return bundleScene(output, materialList, outputMode)

if __name__ == "__main__":
    print(objectLightingTest([0, 0, 0]))

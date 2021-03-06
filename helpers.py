import numpy as np
from math import *

def length(a, b=(0, 0, 0)):
    return np.linalg.norm(np.array(a)-np.array(b))

def swizzle(data, control):
    output = []
    if type(data) == type(0) or type(data) == type(np.float64(0.0)):
        for x in control:
            if x == "x":
                output.append(data)
            else:
                output.append(0)
    elif type(data) == type([]):
        for x in control:
            if x == "x":
                output.append(data[0])
            elif x == "y":
                output.append(data[1])
            elif x == "z":
                output.append(data[2])
            else:
                output.append(0)
    return output

def normalize(array):
    return np.array(array)/np.linalg.norm(array)

def getLine(location, resX, resY):
    base = floor(location/resX)*resX
    return [int(location-base), int(base/resY)]

def pointToUV(point, cameraPosition, resolution):
    rayDir = np.array(point) - np.array(cameraPosition)
    return [(rayDir[0]+1)*(resolution[0]/2), (rayDir[1]+1)*(resolution[1]/2)]

def wrap(x, p): # x is value to be wrapped and p is wrap period
    return x-floor(x/p)*p

def reflect(vector, normal):
    return vector - (2*(np.dot(vector, normal))) * normal

def invSq(dist, mode=0):
    # modes:
    # 0 = standard inv square law, default
    # 1 = approximation of inverse square law, avoids infinity, less accurate
    # 2 = custom
    if mode != 2:
        return (1.0 / ((dist)**2)) if mode == 0 else exp(-dist)*10
    else:
        return 1.0 / (1.0 + dist*0.2 + dist*dist*0.1)

def avg(*args):
    if type(args[0]) == list:
        output = []
        for x in args:
            output = np.array(x) + np.array(output)
        return output / len(args)
    else:
        output = 0
        for x in args:
            output = x + output
        return output / len(args)

# Below function from : https://www.shadertoy.com/view/4tVSDm

def fract(x):
    if type(x) is list or type(x) is np.ndarray:
        return [y - floor(y) for y in x]
    else:
        return x - floor(x)

def hash2(seed):
    return fract(sin(seed+0.1)*np.array((43758.5453123,22578.1459123)))

def cosineWeightedHemisphere(n, seed=0):
    r = hash2(n[0]+n[1]+n[2]+seed)
    uu = normalize( np.cross( n, (0.0,1.0,1.0) ) )
    vv = np.cross( uu, n )
    ra = sqrt(r[1])
    rx = ra*cos(6.2831*r[0])
    ry = ra*sin(6.2831*r[0])
    rz = sqrt( 1.0-r[1] )
    rr = ( rx*uu + ry*vv + rz*n )
    return normalize( rr )

# Above function from : https://www.shadertoy.com/view/4tVSDm

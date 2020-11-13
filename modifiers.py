import numpy as np
from numpy import sin, cos

# Constructive solid geometry

# Only union works at the moment

def opU(a, b): # Union
    return a if a[0] < b[0] else b

def opD(a, b): # Difference
    return max(-a, b)

def opI(a, b): # Intersection
    return max(a, b)

def sminCubic(a, b, r=0.1): # based on github.com/electricsquare/raymarching-workshop
    h = max(r-abs(a-b), 0.0);
    return min(a, b) - h*h*h/(6.0*r*r)

# Translations
def opT(p, t):
    return np.array(p)-np.array(t)

def opR(p, r):
    x, y, z = p[0], p[1], p[2]
    matrix = np.array([x, (y*cos(r))-(z*sin(r)), (y*sin(r))-(z*cos(r))])
    out = matrix
    return out


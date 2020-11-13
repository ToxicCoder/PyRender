import numpy as np
from math import *
from random import randint as rand
import random
# Import custom modules
from sdf import *
from helpers import *
from modifiers import *
from materials import *
from Renderer import *
from scene import objectLightingTest as sdf_scene # cornellBoxV1  scene1 objectLightingTest

def shadeObjectSB(point, lightPos, material, rayDir, hit, reflectionIter=1, bounces=[0, 0], maxBounces=[1, 1], samples=[1, 1]): # Calculate shading for a pixel
    lightPos = np.array(lightPos)
    point = np.array(point)
    lightDir = np.array(normalize(lightPos-point))
    normal = -np.array(calculateNormal(point)) if sdf_scene(point, outputMode=2) else np.array(calculateNormal(point))
    lightDist = length(point, lightPos)

    rayOffset = 0.02

    #colour = np.array([1, 0, 0])

    # Create simple diffuse shading
    lambert = np.dot(normal, lightDir)
    s = rayMarch(point+normal*rayOffset, lightDir, k=10, maxSteps=200, mode=[0, 5]) # Get shadow
    #s[1] = (s[1]+7)*(1/7)#0 if s[0]-lightDist < -7 else 1

    # Diffuse shading
    dif = lambert * s[1]
    dif = np.array([dif, dif, dif])

    # Debugging Data
    lambert = np.array([lambert, lambert, lambert])
    s[1] = np.array([s[1], s[1], s[1]])

    #atten = (1.0 / ((lightDist)**2)) # Inverse square law
    #atten = exp(-lightDist)*10 # Exponent of lightDist multiplied by 10 - similar to inverse square law but no infinity
    atten = 1.0 / (1.0 + lightDist*0.2 + lightDist*lightDist*0.1) # copied - for reference
    lightStrength = 1
    atten = atten * lightStrength

    difGI = np.array([0., 0., 0.])
    if bounces[1] < maxBounces[1]:
        for sample in range(samples[1]):
            giSeed = (point[0]+point[1]+point[2]+sample)**2
            rayDirGI = cosineWeightedHemisphere(calculateNormal(point), seed=giSeed)
            pointGI, hitGI, stepsTakenGI, materialGI, distGI = rayMarch(point+(calculateNormal(point)*0.1), rayDirGI, 50, mode=[1, 2, 4, 6, 0])

            difGInew = shadeObjectSB(pointGI, lightPos, materialGI, rayDirGI, hitGI, reflectionIter=bounces[0], bounces=[bounces[x] + 1 if x == 1 else 0 for x in range(len(bounces))], maxBounces=maxBounces)
            difGInew = difGInew * (materialGI[2] + 1)#(materialGI[2] * 1)
            difGInew = difGInew * np.dot(normal, rayDirGI)
            difGI = difGI + difGInew
        # Proccess difGI
        difGI /= samples[1] # Monte carlo integration
        difGI = difGI # Reduce affect of GI - disabled
        difGI = np.clip(difGI, 0, 1) # Clamp to 0, 1 range - no effect

    #sceneCol = (material[0]*(dif + 0.15) + ((reflectionMaterial[0]*spec*2.0)*(1-material[1])))*atten
    directDif = np.clip((dif * atten), 0, 1)# * material[0]
    
    return (directDif + difGI) * material[0]

# Old, deprecated, may be removed in future versions
def shadeObject(point, lightPos, material, rayDir, hit, reflectionIter=1, bounces=[1, 1]): # Calculate shading for a pixel
    lightPos = np.array(lightPos)
    point = np.array(point)
    lightDir = np.array(normalize(lightPos-point))
    normal = -np.array(calculateNormal(point)) if sdf_scene(point, outputMode=2) else np.array(calculateNormal(point))
    lightDist = length(point, lightPos)

    rayOffset = 0.02

    #colour = np.array([1, 0, 0])

    # Create simple diffuse shading
    lambert = np.dot(normal, lightDir)
    s = rayMarch(point+normal*rayOffset, lightDir, k=10, maxSteps=200, mode=[0, 5]) # Get shadow
    #s[1] = (s[1]+7)*(1/7)#0 if s[0]-lightDist < -7 else 1

    # Diffuse shading
    dif = lambert * s[1]
    dif = np.array([dif, dif, dif])

    # Debugging Data
    lambert = np.array([lambert, lambert, lambert])
    s[1] = np.array([s[1], s[1], s[1]])

    # Specular shading
    if reflectionIter > 0:
        # Trace reflection
        # based on math.stackexchange.com/questions/13261/how-to-get-a-reflection-vector
        reflectionVector = reflect(rayDir, normal)
        reflectionDist, reflectionEnd, reflectionHit, reflectionMaterial = rayMarch(point+normal*rayOffset, reflectionVector, maxSteps=20, mode=[0, 1, 2, 6])
    
        # Specular shade
        spec = shadeObject(reflectionEnd, lightPos, reflectionMaterial, reflectionVector, reflectionHit, reflectionIter=reflectionIter-1)
        #spec = pow(max(np.dot(reflect(-lightDir, calculateNormal(reflectionEnd)), -reflectionVector), 0.0), 8.0)
    else:
        spec = 1.0
        spec = np.array([spec, spec, spec])
        reflectionEnd = point
        reflectionMaterial = material
        roughness = 1.0
    #atten = (1.0 / ((lightDist)**2)) # Inverse square law
    #atten = exp(-lightDist)*10 # Exponent of lightDist multiplied by 10 - similar to inverse square law but no infinity
    atten = 1.0 / (1.0 + lightDist*0.2 + lightDist*lightDist*0.1) # copied - for reference
    lightStrength = 1
    atten = atten * lightStrength

    # [giDist, giDist, giDist]
    sceneCol = (material[0]*(dif + 0.15) + ((reflectionMaterial[0]*spec*2.0)*(1-material[1])))*atten
    return sceneCol#gi+sceneCol#(s[1])#material[0] * (s[1]*50) #sceneCol

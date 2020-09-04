import numpy as np
from math import *
from random import randint as rand
# Import custom modules
from sdf import *
from helpers import *
from modifiers import *
from materials import *
from Renderer import *
from scene import scene1 as sdf_scene # cornellBoxV1  scene1

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

    # Below based os https://www.shadertoy.com/view/Xtt3Wn - it's kinda slow if you open the link

    # Global Illumination / Diffuse Bounces
    giBounce = rayMarch(point+normal*rayOffset, normal, maxSteps=20, mode=[0, 1, 6])
    giDist = invSq(giBounce[0], mode=0)

    # Smooth giDist
    offsets = 0.5
    offsets = [np.array([offsets, 0, 0]),
                np.array([0, offsets, 0]),
                np.array([0, 0, offsets])]
    giDistXp = sdf_scene(giBounce[1]+offsets[0], outputMode=1)
    giDistYp = sdf_scene(giBounce[1]+offsets[1], outputMode=1)
    giDistZp = sdf_scene(giBounce[1]+offsets[2], outputMode=1)

    giDistXn = sdf_scene(giBounce[1]-offsets[0], outputMode=1)
    giDistYn = sdf_scene(giBounce[1]-offsets[1], outputMode=1)
    giDistZn = sdf_scene(giBounce[1]-offsets[2], outputMode=1)

    # Average giDist
    #avgGiDist = giDistXp+giDistYp+giDistZp
    #avgGiDist += giDistXn+giDistYn+giDistZn
    #avgGiDist = avgGiDist / 6

    # Calculate final GI
    gi = np.array(giBounce[2][0]) * giDist

    # [giDist, giDist, giDist]
    sceneCol = (material[0]*(dif + 0.15) + ((reflectionMaterial[0]*spec*2.0)*(1-material[1])))*atten
    return sceneCol#gi+sceneCol#(s[1])#material[0] * (s[1]*50) #sceneCol

def shadeObjectGI(point, lightPos, material, rayDir, camPos, hit, reflectionIter=1, bounces=[1, 1]): # Calculate shading for a pixel
    rayOffset = 0.02

    #colour = np.array([1, 0, 0])
    # Save original ray data
    oRayDir = rayDir
    oCamPos = camPos

    accumulatedColour = np.array([0., 0., 0.])

    for x in range(bounces[1]+1):
        lightPos = np.array(lightPos)
        point = np.array(point)
        lightDir = np.array(normalize(lightPos-point))
        normal = -np.array(calculateNormal(point)) if sdf_scene(point, outputMode=2) else np.array(calculateNormal(point))
        lightDist = length(point, lightPos)

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
        sceneCol = (material[0]*(dif + 0.15) + ((reflectionMaterial[0]*spec*2.0)*(1-material[1])))*atten
        # Add ray colour to accumulatedColour
        weight = 1 if x==0 else 0.5 # Calculate ray weight
        accumulatedColour += sceneCol*weight

        # Calculate new ray
        camPos = point
        rayDir = calculateNormal(point)
        point, material = rayMarch(camPos+normal*rayOffset, rayDir, 50, mode=[1, 6])

    if max(accumulatedColour) > 1:
        print(accumulatedColour)

    sceneCol = accumulatedColour
    return sceneCol#material[0]#gi+sceneCol#(s[1])#material[0] * (s[1]*50) #sceneCol

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

    # [giDist, giDist, giDist]
    sceneCol = (material[0]*(dif + 0.15) + ((reflectionMaterial[0]*spec*2.0)*(1-material[1])))*atten
    return sceneCol#gi+sceneCol#(s[1])#material[0] * (s[1]*50) #sceneCol

def shadeObjectGI(point, lightPos, material, rayDir, hit, reflectionIter=1, bounceWeight=1, bounces=[1, 1], bouncesOrig=[1, 1], samples=[1, 0]): # Calculate shading for a pixel
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

    # Below based on https://www.shadertoy.com/view/Xtt3Wn - it's kinda slow if you open the link

    # Global Illumination / Diffuse Bounces
    if bounces[1] > 0:
        difGI = dif#np.array([0., 0., 0.])
        difSample = np.array([0., 0., 0.])
        samplesTaken = 1
        for sample in range(samples[1]):
            seed = (bounces[1] + sample)**2
            rayDirGI = cosineWeightedHemisphere(calculateNormal(point), seed=seed)
            pointGI, hitGI, stepsTakenGI, materialGI = rayMarch(point+calculateNormal(point)*0.02, rayDir, 50, mode=[1, 2, 4, 6])
            bouncesNew = bounces
            bouncesNew[1] = bouncesNew[1]-1
            if hitGI:
                calcSample = shadeObjectGI(pointGI, lightPos, materialGI, rayDirGI, hitGI, reflectionIter=bounces[0], bounces=bounces, bouncesOrig=bouncesOrig, samples=samples, bounceWeight=bounceWeight/2)
                difSample = difSample + calcSample
                samplesTaken += 1
        difGI = difGI + ((difSample/samplesTaken)*bounceWeight)
    else:
        difGI = [1., 1., 1.]
        materialGI = [[0., 0., 0.], 0.]

    # [giDist, giDist, giDist]
    sceneCol = (materialGI[0]*np.array(difGI))
    #sceneCol = (material[0]*(dif + 0.15) + ((reflectionMaterial[0]*spec*2.0)*(1-material[1])))*atten
    return sceneCol#sceneCol#gi+sceneCol#(s[1])#material[0] * (s[1]*50) #sceneCol

def shadeObjectGIold(point, lightPos, material, rayDir, camPos, hit, reflectionIter=1, bounces=[1, 1], samples=[1, 1]): # Calculate shading for a pixel
    rayOffset = 0.02

    #colour = np.array([1, 0, 0])
    # Save original ray data
    oRayDir = rayDir
    oCamPos = camPos

    accumulatedColour = np.array([1., 1., 1.])

    for x in range(bounces[1]):
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
        accumulatedColour += sceneCol#*weight

        # Calculate new ray
        avgMat = [np.array([0, 0, 0]), 0]
        for sampleIndex in range(samples[1]):
            camPos = point
            seed = sampleIndex+accumulatedColour[0]#*(rayDir[0]+rayDir[1]-rayDir[2])
            rayDir = cosineWeightedHemisphere(calculateNormal(point), seed=seed)
            point, material = rayMarch(camPos+normal*rayOffset, rayDir, 50, mode=[1, 6])
            #avgMat[0] = np.array(avgMat[0]) + material[0]
            #avgMat[1] += material[1]

        
        # Calculate average material from samples
        #avgMat[0] = np.array(avgMat[0]) / (samples[1]+1)
        #avgMat[1] /= (samples[1]+1)

       #material = avgMat

    if max(accumulatedColour) > 1:
        print(accumulatedColour)

    sceneCol = accumulatedColour
    return sceneCol#material[0]#gi+sceneCol#(s[1])#material[0] * (s[1]*50) #sceneCol

def shadeObjectGInew(point, lightPos, material, rayDir, hit, reflectionIter=1, bounces=[1, 1], samples=[1, 1]): # Calculate shading for a pixel
    if not hit:
        return np.array([0, 0, 0])
    origPoint = point
    origRayDir = rayDir
    sceneColListTotal = []
    for sample in range(samples[1]):
        sceneColList = []
        for bounce in range(bounces[1]+1):
            giSeed = sample+bounce+(origPoint[0]+origPoint[1]+origPoint[2])
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
            sceneColList.append(sceneCol)

            # Calculate next ray
            rayDir = cosineWeightedHemisphere(calculateNormal(point), seed=giSeed)
            point, hit, stepsTaken, material = rayMarch(point+calculateNormal(point)*0.02, rayDir, 50, mode=[1, 2, 4, 6])
        #sceneCol = np.array([0, 0, 0])
        sceneCol = sceneColList[0]
        colWeight = 1
        for col in sceneColList[::-1]:
            sceneCol = (sceneCol+col)/2#sceneCol+(col*colWeight)
            colWeight *= 0.8
        sceneColListTotal.append(sceneCol)
    #sceneCol = np.array([0, 0, 0])
    sceneCol = sceneColListTotal[0]
    colWeight = 1
    for col in sceneColListTotal[::-1]:
        sceneCol = (sceneCol+col)/2#sceneCol+(col*colWeight)
        colWeight *= 0.8
    return sceneCol#gi+sceneCol#(s[1])#material[0] * (s[1]*50) #sceneCol

def shadeObjectSB(point, lightPos, material, rayDir, hit, reflectionIter=1, bounces=[1, 1], samples=[1, 1]): # Calculate shading for a pixel
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

    difGI = np.array([0., 0., 0.])
    for sample in range(samples[1]):
        giSeed = (point[0]+point[1]+point[2]+sample)**2
        rayDirGI = cosineWeightedHemisphere(calculateNormal(point), seed=giSeed)
        pointGI, hitGI, stepsTakenGI, materialGI, distGI = rayMarch(point+(calculateNormal(point)*0.1), rayDirGI, 50, mode=[1, 2, 4, 6, 0])

        difGInew = shadeObject(pointGI, lightPos, materialGI, rayDirGI, hitGI, reflectionIter=bounces[0], bounces=bounces)
        difGInew = difGInew * np.dot(normal, rayDirGI)
        difGI = difGI + difGInew
    # Proccess difGI
    difGI /= samples[1] # Monte carlo integration
    difGI = difGI # Reduce affect of GI
    difGI = np.clip(difGI, 0, 1) # Clamp to 0, 1 range

    # [giDist, giDist, giDist]
    sceneCol = (material[0]*(dif + 0.15) + ((reflectionMaterial[0]*spec*2.0)*(1-material[1])))*atten
    directDif = (dif * atten) * material[0]
    #return difGI+sceneCol#sceneCol+difGI#gi+sceneCol#(s[1])#material[0] * (s[1]*50) #sceneCol
    return difGI
    #return difGI + directDif

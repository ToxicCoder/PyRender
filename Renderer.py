# import modules for multiprocessing support
from multiprocessing import Pool
# Matplotlib to display final rendered image
import matplotlib.pyplot as plt
# Extras
from functools import partial
import numpy as np
from math import *
import time

# Import custom modules
from sdf import *
from helpers import *
from modifiers import *
from materials import *
from shadingFunctions import *
from scene import scene1 as sdf_scene # cornellBoxV1  scene1

# Rendering functions
def rayMarch(start, directionVector, maxSteps=100, clipStart=0, clipEnd=1000, accuracy=0.0001, k=4, mode=[0]): # Multiuse raymarching function
    # mode 0 = return distance
    # mode 1 = return endpoint
    # mode 2 = return point and hit
    # mode 3 = return min distance
    # mode 4 = return # of steps
    # mode 5 = return shadows
    # mode 6 = return material
    point = start
    distTravelled = 0
    minDistance = sdf_scene(point)
    numSteps = 0
    shadow = 1
    #pDist = 1e20
    for x in range(maxSteps):
        dist = sdf_scene(point) # Get distance to scene
        point = np.array(point) + np.array([x*dist for x in directionVector]) # Move along ray
        distTravelled += dist # Add distance to the total distance counter
        if dist < minDistance: # Update minimum distance
            minDistance = dist
        numSteps += 1
        if abs(dist) < accuracy or distTravelled > clipEnd or dist > clipEnd:
            break
        #y = dist*dist/(2.0*pDist)
        #try:
        #    d = sqrt(dist*dist-y*y)
        #except:
        #    pass
        #shadow = min(shadow, k*d/max(0.0,distTravelled-y))
        shadow = min(shadow, k * dist / distTravelled) # Based on www.iquilezles.org/www/articles/rmshadows/rmshadows.htm
        #pDist = dist
    outputs = []
    for x in mode:
        if x == 0:
            outputs.append(dist)
        elif x == 1:
            outputs.append(point)
        elif x == 2:
            outputs.append(dist<clipEnd and dist>clipStart)
        elif x == 3:
            outputs.append(minDistance)
        elif x == 4:
            outputs.append(numSteps)
        elif x == 5:
            outputs.append(shadow)
        elif x == 6:
            material = sdf_scene(point, outputMode=1)
            outputs.append((np.array(material[0]), material[1]))
    if len(outputs) == 1:
        return outputs[0]
    return outputs

def calculateNormal(point, epsilon=0.001): # epsilon is arbitrary — should be smaller than any surface detail in your distance function, but not so small as to get lost in float precision
    centerDistance = sdf_scene(point)
    xDistance = sdf_scene(np.array(point) + np.array((epsilon, 0, 0)))
    yDistance = sdf_scene(np.array(point) + np.array((0, epsilon, 0)))
    zDistance = sdf_scene(np.array(point) + np.array((0, 0, epsilon)))
    normal = ((xDistance, yDistance, zDistance) - centerDistance) / epsilon
    return normal

def renderPixel(x, y, resolution, cameraPosition, steps, lightPos, aspectRatio): # Render individual pixel and return colour value
    xMax = 1*aspectRatio
    yMax = 1/aspectRatio
    rayDir = [x/(resolution[0]/(xMax*2))-xMax, -1, y/(resolution[1]/(yMax*2))-yMax]
    rayPoint, hit, stepsTaken, material = rayMarch(cameraPosition, rayDir, steps, mode=[1, 2, 4, 6])
    #return [rayMarch(cameraPosition, rayDir, steps), 0, 0]
    bounces=[0, 1] # order - glossy, diffuse
    samples=[1, 1] # order - Same as above
    #dif = shadeObject(rayPoint, lightPos, material, rayDir, hit, reflectionIter=bounces[0], bounces=bounces)
    #dif = shadeObjectGI(rayPoint, lightPos, material, rayDir, hit, reflectionIter=bounces[0], bounces=bounces, bouncesOrig=bounces, samples=samples)
    #dif = shadeObjectGIold(rayPoint, lightPos, material, rayDir, cameraPosition, hit, reflectionIter=bounces[0], bounces=bounces)
    #dif = shadeObjectGI(rayPoint, lightPos, material, rayDir, cameraPosition, hit, reflectionIter=bounces[0], bounces=bounces, samples=samples)
    #dif = shadeObjectGInew(rayPoint, lightPos, material, rayDir, hit, reflectionIter=bounces[0], bounces=bounces, samples=samples)
    dif = shadeObjectSB(rayPoint, lightPos, material, rayDir, hit, reflectionIter=bounces[0], bounces=bounces, samples=samples)
    return dif
    #return calculateNormal(rayMarch(cameraPosition, rayDir, steps, mode=1))

def singlePixelMap(resolution, cameraPosition, steps, lightPos, aspectRatio, x): # Run "renderPixel" function - used in "pool.map" for multiprocessing
    xPos, yPos = getLine(x, resolution[0], resolution[1])
    col = renderPixel(xPos, yPos, resolution, cameraPosition, steps, lightPos, aspectRatio)
    col = [pow(abs(x), 1/2.2)*np.sign(x) for x in col] # Apply gamma correction
    return col

if __name__ == "__main__":
    # Setup scene info
    cameraPosition = [0, 4, 2]
    lightPos = [0, 0, 4]
    
    # Set render parameters
    steps = 50
    resolution = [100, 100]
    aspectRatio = resolution[0]/resolution[1]

    # Start timer
    renderStart = time.time()
    # Setup pool
    pool = Pool(8)
    # Add arguments to render function
    singlePixelMapPartial = partial(singlePixelMap, resolution, cameraPosition, steps, lightPos, aspectRatio)
    # Render image using pool
    renderedImage = pool.map(singlePixelMapPartial, range(resolution[0]*resolution[1]))

    # Shape conversion
    final = []
    for x in range(resolution[0]):
        final.append([])
        for y in range(resolution[1]):
            final[x].append(np.clip(renderedImage[x+(y*resolution[0])], 0, 1))
    
    final = np.rot90(final) # By default image is rendered sideways
    
    renderEnd = time.time() # End timer
    timeTaken = renderEnd-renderStart
    print(f"Rendering time : {timeTaken} : {floor(timeTaken/60)} min {round(((timeTaken/60)-floor(timeTaken/60))*60)} s") # Print time taken in seconds

    # Optionally save the image to a file
    plt.imsave("Renders/render.png", final)

    # Display rendered & processed image
    fig, ax = plt.subplots()
    im = ax.imshow(final)
    plt.show()

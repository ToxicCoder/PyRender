# TAA - Terrible Anti Aliasing

# Matplotlib to display output
import matplotlib.pyplot as plt
# Import PIL to import the image
from PIL import Image
import PIL
# Import numpy to handle arrays
import numpy as np
from numpy import clip
# Import time to mesure time taken
import time

# Define functions
def getLuminance(RGB):
    l = (0.2126*RGB[0] + 0.7152*RGB[1] + 0.0722*RGB[2])
    return l

# Read in image
imPath = "Renders/render.png"
imIn = Image.open(imPath)
# Convert PIL to nump array
img = np.asarray(imIn)/255 # /255 to convert from 8-bit to float

start = time.time()

# Get luminance from image
luminance = np.array([[getLuminance(y) for y in x] for x in img])

# Get resolution
resolution = [len(luminance), len(luminance[0])]
print(resolution)

edges = []
final = []

for x in range(resolution[0]):
    #edges.append([])
    final.append([])
    for y in range(resolution[1]):
        C = luminance[x][y]
        N = luminance[clip(x, 0, resolution[0]-1)][clip(y+1, 0, resolution[1]-1)]-C
        E = luminance[clip(x+1, 0, resolution[0]-1)][clip(y, 0, resolution[1]-1)]-C
        S = luminance[clip(x, 0, resolution[0]-1)][clip(y-1, 0, resolution[1]-1)]-C
        W = luminance[clip(x-1, 0, resolution[0]-1)][clip(y, 0, resolution[1]-1)]-C
        #edges[x].append(N+E+S+W)
        edge = N+E+S+W
        C = img[x][y]
        N = img[clip(x, 0, resolution[0]-1)][clip(y+1, 0, resolution[1]-1)]
        E = img[clip(x+1, 0, resolution[0]-1)][clip(y, 0, resolution[1]-1)]
        S = img[clip(x, 0, resolution[0]-1)][clip(y-1, 0, resolution[1]-1)]
        W = img[clip(x-1, 0, resolution[0]-1)][clip(y, 0, resolution[1]-1)]
        final[x].append(((C+N+E+S+W)/5) if abs(edge) > 0.1 else C)

final = np.array(final)

end = time.time()

timeTaken = end-start

print(f"Time Taken : {timeTaken} : {np.floor(timeTaken/60)} min {round(((timeTaken/60)-np.floor(timeTaken/60))*60)} s")

# Export image
plt.imsave(imPath.replace(".", "_AA."), final)

# Display processed image
fig, ax = plt.subplots()
im = ax.imshow(final)
plt.show()

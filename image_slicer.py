import cv2
import glob
import numpy as np
import sys
from matplotlib import pyplot as plt 
import ipywidgets as ipyw

import numpy as np
import matplotlib.pyplot as plt





class IndexTracker:
    def __init__(self, ax, X):
        self.ax = ax
        ax.set_title('use arrow keys to navigate images')

        self.X = X
        self.slices = X.shape[0]
        self.rows = X.shape[1]
        self.cols  = X.shape[2]
        self.ind = self.slices//2

        self.im = ax.imshow(self.X[self.ind, :, :])
        self.update()

    def on_scroll(self, event):
        print("%s" % (event.key))
        if event.key == 'right':
            self.ind = (self.ind + 1) % self.slices
        elif event.key == 'left':
            self.ind = (self.ind - 1) % self.slices
        self.update()

    def update(self):
        self.im.set_data(self.X[self.ind, :, :])
        self.ax.set_ylabel('projection %s' % self.ind)
        self.im.axes.figure.canvas.draw()




image_list = []
file_path = "C:/Users/Naomi/pythonproj/Tomografia_Darth_Vader/*.tiff" #sys.argv[0]

for filename in glob.glob(file_path): #assuming tiff
    im=cv2.imread(filename,0) #0 stands for the gray_image reading (default is RGB reading)
    image_list.append(im)

new_image_list = np.asarray(image_list)

fig, ax = plt.subplots(1, 1)
tracker = IndexTracker(ax, new_image_list)
fig.canvas.mpl_connect('key_press_event', tracker.on_scroll)
plt.show()


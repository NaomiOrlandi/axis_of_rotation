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

        self.im = ax.imshow(self.X[self.ind, :, :],cmap='gray')
        self.update()

    def on_scroll(self, event):
        '''
        This method allows to scroll through the successive image pressing the right arrow key on the keyboard
        and to scroll through the previous image pressing the left arrow key on the keyboard
        '''
        if event.key == 'right':
            self.ind = (self.ind + 1) % self.slices
        elif event.key == 'left':
            self.ind = (self.ind - 1) % self.slices
        self.update()

    def update(self):
        self.im.set_data(self.X[self.ind, :, :])
        self.ax.set_ylabel('projection %s' % self.ind)
        self.im.axes.figure.canvas.draw()



def plot_tracker (img_array):
    '''
    This method shows a stack of images with the possibility to 
    scroll through the images pressing the right or left arrow key on the keyboard
    
    Parameters
    ----------
    img_array : ndarray
        three dimensional stack of images
    '''
    fig, ax = plt.subplots(1, 1)
    tracker = IndexTracker(ax, img_array)
    fig.canvas.mpl_connect('key_press_event', tracker.on_scroll)
    plt.show()

import matplotlib.pyplot as plt


class IndexTracker:
    '''
    In this class all the characteristics for the visualization of 
    a stack of images are set.

    Methods
    ------------
    __init__(self,ax,X)
        initialize the image window with a specific title and structure.
        The visualization of images in a stack starts with the image in the middle.
    
    on_scroll(self,ax,X)
        allows to scroll through the images pressing the right/left arrow key on the keyboard.

    update(self,event)
        updates the visualized slice and the label on the y-axis.
    '''
    def __init__(self, ax, X):
        '''
        this method create a image window with title 'use arrow keys to navigate images'
        to show in gray-level map the stack X, which has 3 dimensions, one for the slices, one for 
        the rows and one for the columns.
        The visualization starts with the slice in the middle of the stack.
        '''

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
        '''
        This method updates the visualized slice and the label
        of y-axis when the slice changes.'''

        self.im.set_data(self.X[self.ind, :, :])
        self.ax.set_ylabel('projection %s' % self.ind)
        self.im.axes.figure.canvas.draw()



def plot_tracker (img_array):
    '''
    This function shows a stack of images with the possibility to 
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

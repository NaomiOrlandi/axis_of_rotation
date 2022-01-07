import os
from tkinter import filedialog

'''
This program can be usefull to change the 
numbering of the .tiff images that will be read by 
preparation_data.reader_gray_images() function.
Hence, a orderly reading and successive showing of images
can be obtained.
The program let the user select the directory containing the files
through a dialog window.
Then just the files not starting with '.' or '_' are selected.
So, depending on the desired number of digits for the numbering of
files, the latters will be renamed with the same prefix and changed
numbering.

Example
-------
image_1, image_2, ..., image_16 ------> image_01, image_02, ..., image 16.

Note
----
zeros che be just added, not removed.
'''
cleaned_files = []

root_folder = filedialog.askdirectory()
os.chdir(root_folder)
folder_files = os.listdir(root_folder)

# Filter out files starting with '.' and '_'
cleaned_files = []
for item in folder_files:
    if item[0] == '.' or item[0] == '_':
        pass
    else:
        cleaned_files.append(item)

def getFiles(cleaned_files):
    '''
    This function take as input a list of files, split the filenames 
    according to a certain symbol expressed in file.split('symbol'),
    then change the final part of the name adding zeros at the beginning
    untill filling the number of characters specified in zfill(total num of characters).
    At the end files are renamed.
    
    Parameters
    ----------
    cleaned_files : list
        list of strings representing files
    '''
    for file in cleaned_files:
        old_filename = os.path.basename(file)
        
        file_start = file.split('_')[0] #file start before _
        file_number= file.split('_')[1] #file number + extention
        num = str(file_number).zfill(8)  # num is 8 characters long with leading 0
        
        new_file = "{0}_{1}".format(file_start, num)
        #rename the files
        os.rename(old_filename,new_file)
        
getFiles(cleaned_files)
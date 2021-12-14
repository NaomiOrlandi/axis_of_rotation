import os
from tkinter import filedialog

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
    for file in cleaned_files:
        old_filename = os.path.basename(file)
        #extention = old_filename.split('.')[-1]
        file_start = file.split('_')[0] #file start before _
        file_number= file.split('_')[-1] #file number + extention
        num = file_number.zfill(9)  # num is 9 characters long with leading 0

        new_file = "{}_{}".format(file_start, num)
        #rename the files
        os.rename(old_filename,new_file)
        
getFiles(cleaned_files)
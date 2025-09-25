import glob
import os
import global_config
import mgr_mp4 as make_anim

# file path seperator / or \ ???
pathsep = os.sep

def local_file_list_build(directory):
    # Builds and returns a list of files contained in the directory.
    # List is sorted into A --> Z order
    dirlisting = []
    path = directory + pathsep + "*.*"
    for name in glob.glob(path):
        name = os.path.normpath(name)
        dirlisting.append(name)
    dirlisting.sort()
    return dirlisting


if __name__ == '__main__':
        # data = global_config.noaa_image_data
        # store = 1
        # diffs = 2

        # Make animations
        folder = global_config.folder_source_images + os.sep + 'custom'
        img_files = local_file_list_build(folder)
        # a day is roughly 360 images
        img_files = img_files[-360:]
        outputfile = global_config.folder_output_to_publish + os.sep + 'custom'
        make_anim.wrapper(img_files, outputfile)
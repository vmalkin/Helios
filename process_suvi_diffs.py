import cv2
import time
import datetime
from calendar import timegm
import numpy as np
import global_config
import os
import glob

goes_dict = global_config.goes_dict

def local_file_list_build(directory):
    # Builds and returns a list of files contained in the directory.
    # List is sorted into A --> Z order
    dirlisting = []
    path = directory + os.sep + "*.*"
    for name in glob.glob(path):
        name = os.path.normpath(name)
        dirlisting.append(name)
    dirlisting.sort()
    return dirlisting


def posix2utc(posixtime, timeformat):
    # '%Y-%m-%d %H:%M'
    # utctime = datetime.datetime.utcfromtimestamp(int(posixtime)).strftime(timeformat)
    utctime = datetime.datetime.fromtimestamp(int(posixtime), datetime.UTC).strftime(timeformat)
    return utctime


def median_image(img_1, img_2, img_3):
    # img_1 = img_1.astype(int)
    # img_2 = img_2.astype(int)
    # img_3 = img_3.astype(int)
    t = [img_1, img_2, img_3]
    p = np.median(t, axis=0)
    return p


def utc2posix(utcstring, timeformat):
    utc_time = time.strptime(utcstring, timeformat)
    epoch_time = timegm(utc_time)
    return epoch_time

def create_label(image, timestamp, wavelength):
    # width, height, channels = image.shape
    width, height = image.shape
    label_height = int(height / 10)
    font_height = int(height / 12)
    cv2.rectangle(image, (0,0), (width,label_height), (0, 0, 0), -1)
    cv2.rectangle(image, (0, height - label_height), (width, height), (0, 0, 0), -1)

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_size = 1
    # colours are blue, green, red in opencv
    font_color = (255, 255, 255)
    font_thickness = 1
    label0 = "GOES SUVI " + str(wavelength) + "A image."
    label1 = "Image time: " + timestamp
    label2 = "Images courtesy of NOAA." + global_config.copyright
    cv2.putText(image, label0, (0, 50), font, font_size, font_color, font_thickness, cv2.LINE_AA)
    cv2.putText(image, label1, (0, 100), font, font_size, font_color, font_thickness, cv2.LINE_AA)
    cv2.putText(image, label2, (0, height - 80), font, font_size, font_color, font_thickness, cv2.LINE_AA)
    return image

def image_read_fromfile(name):
    # Colour?
    # image = cv2.imread(name)

    # Greyscale?
    image = cv2.imread(name, 0)
    return image

def image_translate(imagename, translation_value):
    # translation_value is the number of rows (x and y)
    # we want to shift the image by.
    # Remove 2 rows/cols at end and add 2 rows/cols at beginning

    # width, height, channels = image.shape
    width, height = imagename.shape

    # delete columns axis = 1
    for i in range(0, translation_value):
        imagename = np.delete(imagename, [width - translation_value], axis=1)
    # delete rows axis = 0
    for i in range(0, translation_value):
        imagename = np.delete(imagename, [width - translation_value], axis=0)

    # insert columns
    for i in range(0, translation_value):
        # img_new = np.insert(img_new, 0, [0, 0, 0], axis=1)
        imagename = np.insert(imagename, 0, [0], axis=1)
    # insert rows
    for i in range(0, translation_value):
        imagename = np.insert(imagename, 0, imagename[0], axis=0)

    return imagename


def create_reticle(image):
    solar_diameter = 400
    width, height = image.shape
    x_offset = 0
    y_offset = 0
    x_centre = int(width / 2) + x_offset
    y_centre = int(height / 2) + y_offset
    cv2.circle(image, (x_centre, y_centre), solar_diameter, (0, 100, 0), 3)
    return image


def wrapper(filepathlist, diffstore, pathsep, wavelength):
    print("*** Differencing STARTED ", diffstore)
    processing_store = []
    for i in range(1, len(filepathlist)):
        old_name = filepathlist[i - 1]
        ot1 = old_name.split("_s")
        ot2 = ot1[2].split("_e")
        old_time = utc2posix(ot2[0], "%Y%m%dT%H%M%SZ")

        new_name = filepathlist[i]
        nt1 = new_name.split("_s")
        nt2 = nt1[2].split("_e")
        new_time = utc2posix(nt2[0], "%Y%m%dT%H%M%SZ")

        # large gaps im image times should NOT be diffrenced
        if (new_time - old_time) < (60 * 10):
            # https: // stackoverflow.com / questions / 58638506 / how - to - make - a - jpg - image - semi - transparent
            # Make image 50% transparent
            img_old = image_read_fromfile(old_name)

            # invert one image
            img_new = image_read_fromfile(new_name)
            img_new = cv2.bitwise_not(img_new)
            # img_new = image_translate(img_new, 1)

            try:
                # img_diff = np.add(img_old, img_new)
                img_diff = cv2.addWeighted(img_old, 0.5, img_new, 0.5, 0)
                # img_diff = cv2.absdiff(img_old,img_new)
                img_diff = cv2.medianBlur(img_diff, 3)


                clahe = cv2.createCLAHE(clipLimit=32, tileGridSize=(10, 10))
                img_diff = clahe.apply(img_diff)

                # # Add watermark to image
                # timestamp = posix2utc(new_time, "%Y-%m-%d %H:%M UTC")
                # img_diff = create_label(img_diff, timestamp)
                # img_diff = create_reticle(img_diff)
                #
                # # Give the file the UTC time of the start of the observation
                diff_filename = diffstore + pathsep + ot2[0] + "_df.png"
                tmp = [diff_filename, old_time, img_diff]
                processing_store.append(tmp)
                # cv2.imwrite(diff_filename, img_diff)
            except:
                print("!!! Image differencing failed for ", new_name)

    # Apply a median filter to an array of stored images to reduce speckle
    for i in range(2, len(processing_store)):
        filename = processing_store[i-1][0]
        posixtime = processing_store[i-1][1]
        timestamp = posix2utc(posixtime, '%Y-%m-%d %H:%M')
        img1 = processing_store[i][2]
        img2 = processing_store[i-1][2]
        img3 = processing_store[i-2][2]
        filtered_img = median_image(img1, img2, img3)

        # Adjust the brightness and contrast
        # Adjusts the brightness by adding 10 to each pixel value
        brightness = -150
        # Adjusts the contrast by scaling the pixel values by 2.3
        contrast = 2
        filtered_img = cv2.addWeighted(filtered_img, contrast, np.zeros(filtered_img.shape, filtered_img.dtype), 0, brightness)

        # filtered_img = cv2.normalize(filtered_img, None, 50, 250, cv2.NORM_MINMAX)

        filtered_img = create_label(filtered_img, timestamp, wavelength)
        filtered_img = create_reticle(filtered_img)
        cv2.imwrite(filename, filtered_img)

    print("*** Differencing FINISHED")

if __name__ == '__main__':
    # Calculate difference images for each wavelength
    for sat in goes_dict:
        for key in goes_dict[sat]['wavelengths']:
            name = sat
            image_diffs = goes_dict[sat]['wavelengths'][key]['diffs']
            image_store = goes_dict[sat]['wavelengths'][key]['store']

            img_files = local_file_list_build(image_store)
            img_files = img_files[-360:]
            wrapper(img_files, image_diffs, os.sep, name)
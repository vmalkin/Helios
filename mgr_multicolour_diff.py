import os
import cv2
import datetime
import time
from calendar import timegm
import numpy as np

import global_config

pathsep = os.sep


def create_label(image, timestamp):
    # width, height, channels = image.shape
    width, height, depth = image.shape
    label_height = int(height / 10)
    font_height = int(height / 12)
    cv2.rectangle(image, (0,0), (width,label_height), (0, 0, 0), -1)
    cv2.rectangle(image, (0, height - label_height), (width, height), (0, 0, 0), -1)

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_size = 1
    # colours are blue, green, red in opencv
    font_color = (255, 255, 255)
    font_thickness = 1
    label0 = "GOES SUVI false colour differences image."
    label1 = "Image time: " + timestamp
    label2 = "Images courtesy of NOAA." + global_config.copyright
    cv2.putText(image, label0, (0, 50), font, font_size, font_color, font_thickness, cv2.LINE_AA)
    cv2.putText(image, label1, (0, 100), font, font_size, font_color, font_thickness, cv2.LINE_AA)
    cv2.putText(image, label2, (0, height - 80), font, font_size, font_color, font_thickness, cv2.LINE_AA)
    return image


def posix2utc(posixtime, timeformat):
    # '%Y-%m-%d %H:%M'
    utctime = datetime.datetime.utcfromtimestamp(int(posixtime)).strftime(timeformat)
    return utctime


def utc2posix(utcstring, timeformat):
    utc_time = time.strptime(utcstring, timeformat)
    epoch_time = timegm(utc_time)
    return epoch_time


def wrapper(multifilelist, save_folder):
    print('*** BEGIN multicolour diffs processing ', save_folder)

    if os.path.exists(save_folder) is False:
        os.makedirs(save_folder)

    for item in multifilelist:
        files = item
        # print(files)
        if len(files) == 3:
            # splitvalue = '_' + '|' +  str(pathsep)
            # print(splitvalue)

            t = files[0].split(pathsep)
            tt = t[2].split('_')
            timestamp = tt[0]
            filename = timestamp + '.png'
            timestamp = utc2posix(timestamp, '%Y%m%dT%H%M%SZ')
            timestamp = posix2utc(timestamp, '%Y-%m-%d %H:%M')

            b = cv2.imread(files[0], 0)
            r = cv2.imread(files[1], 0)
            g = cv2.imread(files[2], 0)
            colour_img = cv2.merge([b, g, r])
            colour_img = create_label(colour_img, timestamp)

            # Adjust the brightness and contrast
            # Adjusts the brightness by adding 10 to each pixel value
            brightness = -150
            # Adjusts the contrast by scaling the pixel values by 2.3
            contrast = 2
            colour_img = cv2.addWeighted(colour_img, contrast, np.zeros(colour_img.shape, colour_img.dtype), 0,
                                           brightness)

            # colour_img = cv2.cvtColor(colour_img, cv2.COLOR_BGR2GRAY)
            fc = save_folder + pathsep + str(filename)
            cv2.imwrite(fc, colour_img)


    print('*** END multicolour diffs processing')

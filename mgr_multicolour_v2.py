import os
import cv2
import datetime
import time
from calendar import timegm
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
    label0 = "GOES SUVI 171A, 195A, 284A false colour image."
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
    print('*** BEGIN multicolour processing ', save_folder)

    if os.path.exists(save_folder) is False:
        os.makedirs(save_folder)

    for item in multifilelist:
        files = item
        # print(files)
        if len(files) == 3:
            f = files[0].split(os.sep)
            t = f[2].split('_')
            timestamp = t[3][1:-1]
            # print(timestamp)
            filename = timestamp + '_clr.png'

            timestamp = utc2posix(timestamp, '%Y%m%dT%H%M%S')
            timestamp = posix2utc(timestamp, '%Y-%m-%d %H:%M')

            b = cv2.imread(files[0], 0)
            r = cv2.imread(files[1], 0)
            g = cv2.imread(files[2], 0)
            try:
                # colour_img = cv2.merge([g, b, r])
                # b,r,r emphasises coronal holes.
                colour_img = cv2.merge([b, r, r])

                colour_img = create_label(colour_img, timestamp)
                fc = save_folder + pathsep + str(filename)
                cv2.imwrite(fc, colour_img)
            except cv2.error:
                print('!!! Unable to merge files to colour image')


    print('*** END multicolour processing')

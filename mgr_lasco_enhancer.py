import cv2
import os
import glob
import datetime
import calendar
import numpy as np
import math
import time
from PIL import Image

import global_config


def add_stamp(banner_text, image_object, filename):
    tt = time.time()
    tt = posix2utc(tt, "%Y-%m-%d %H:%M")
    cv2. rectangle(image_object, (0, 449), (511, 511), (255, 255, 255), -1)
    cv2.rectangle(image_object, (0, 0), (511, 20), (255, 255, 255), -1)
    colour = (0, 0, 0)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_size = 0.5
    font_color = colour
    font_thickness = 1
    banner = banner_text
    x, y = 5, 15
    cv2.putText(image_object, banner, (x, y), font, font_size, font_color, font_thickness, cv2.LINE_AA)

    banner = 'LASCO coronagraph. Updated ' + tt + " UTC."
    x, y = 5, 466
    cv2.putText(image_object, banner, (x, y), font, font_size, font_color, font_thickness, cv2.LINE_AA)

    font_size = 0.4
    font_color = colour
    font_thickness = 1

    banner = filename
    x, y = 5, 483
    cv2.putText(image_object, banner, (x, y), font, font_size, font_color, font_thickness, cv2.LINE_AA)
    banner = 'Courtesy of SOHO/LASCO consortium. SOHO is a project of'
    x, y = 5, 496
    cv2.putText(image_object, banner, (x, y), font, font_size, font_color, font_thickness, cv2.LINE_AA)
    banner = 'international cooperation between ESA and NASA'
    x, y = 5, 508
    cv2.putText(image_object, banner, (x, y), font, font_size, font_color, font_thickness, cv2.LINE_AA)


def posix2utc(posixtime, timeformat):
    # '%Y-%m-%d %H:%M'
    utctime = datetime.datetime.utcfromtimestamp(int(posixtime)).strftime(timeformat)
    return utctime


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

# def get_dirlisting(folder):
#     dirlisting = []
#     path = os.path.join(folder, "*.jpg")
#     for name in glob.glob(path):
#         name = os.path.normpath(name)
#         seperator = os.path.sep
#         n = name.split(seperator)
#         nn = n[1]
#         dirlisting.append(nn)
#         # make sure they are in chronological order by name
#     dirlisting.sort()
#     return dirlisting

def shorten_dirlisting(processing_start_date, directory_listing):
    # Return files for the last x hours, as needed.
    # cutoff = processing_start_date
    # returnarray = []
    # for item in directory_listing:
    #     dt = filename_converter(item, "posix")
    #     if dt > cutoff:
    #         returnarray.append(item)
    returnarray = directory_listing[-360:]
    return returnarray


def filename_converter(filename, switch="posix"):
    # Name has format 20221230_2342_c3_512.jpg
    f = filename.split("_")

    yyyymmdd = f[0]
    hhmm = f[1]
    year = (yyyymmdd[:4])
    month = (yyyymmdd[4:6])
    day = (yyyymmdd[6:])
    hour = (hhmm[:2])
    min = (hhmm[2:])
    utc_string = year + '-' + month + '-' + day + ' ' + hour + ':' + min
    filename = year + '-' + month + '-' + day + '-' + hour + '-' + min + ".jpg"
    # utc time string
    dt = datetime.datetime.strptime(utc_string, '%Y-%m-%d %H:%M')

    if switch == "utc":
        # utc time string
        returnstring = datetime.datetime.strptime(utc_string, '%Y-%m-%d %H:%M')
    elif switch == "filename":
        returnstring = filename
    else:
        returnstring = calendar.timegm(dt.timetuple())
    # return posix by default
    return returnstring


def colourise(final):
    new_image = cv2.applyColorMap(final, cv2.COLORMAP_OCEAN)
    return new_image


def median_image(img_1, img_2, img_3):
    try:
        t = [img_1, img_2, img_3]
        p = np.median(t, axis=0)
    except:
        print('Unable to apply median filter to images')
        p = None
    return p


def wrapper(processing_start_date, lasco_folder, enhanced_folder):
    print("*** Enhancer: Start")
    time_threshold = 60 * 120
    # get image list of LASCO files for the last x-hours.
    dirlisting = local_file_list_build(lasco_folder)
    dirlisting = shorten_dirlisting(processing_start_date, dirlisting)

    print("Most recent file: ", dirlisting[len(dirlisting) - 1])
    print("Starting at file: ", dirlisting[0])
    anim_enhanced = []
    anim_lasco = []

    file = lasco_folder + os.sep + dirlisting[0]
    image_accumulated = cv2.imread(file, 0)

    # if time difference between img_x, ing_y < time threshold
    print("*** Enhancer: Removing particle hits from files")
    for i in range(1, len(dirlisting) - 1):
        f1 = dirlisting[i - 1].split(os.sep)
        f2 = dirlisting[i].split(os.sep)
        f3 = dirlisting[i + 1].split(os.sep)
        file_1 = f1[2]
        file_2 = f2[2]

        if filename_converter(file_2, "posix") - filename_converter(file_1, "posix") < time_threshold:
            img_1 = cv2.imread(dirlisting[i - 1], 0)
            img_2 = cv2.imread(dirlisting[i], 0)
            img_3 = cv2.imread(dirlisting[i + 1], 0)
            picture = median_image(img_1, img_2, img_3)

            if picture is not None:
                # alpha value [1.0-3.0] CONTRAST
                # beta value [0-100] BRIGHTNESS
                alpha = 1.5
                beta = 2
                picture = cv2.convertScaleAbs(picture, alpha=alpha, beta=beta)
                clahe = cv2.createCLAHE(clipLimit=2, tileGridSize=(10,10))
                picture = clahe.apply(picture)

                # picture = cv2.bitwise_not(picture)
                picture = colourise(picture)
                text = 'Processed at ' + global_config.copyright
                add_stamp(text, picture, dirlisting[i])
                savefile = enhanced_folder + os.sep + file_2
                cv2.imwrite(savefile, picture)

    print("*** Enhancer: Finished")
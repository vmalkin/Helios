# -*- coding: utf-8 -*-
# Solar Image Parser v0.1
# Designed to process an EUV image from a live URL 
# to display probably coronal hole locations. 
# uses the OpenCV library and based on the work of Rotter, Veronig, Temmer & Vrsnak
# http://oh.geof.unizg.hr/SOLSTEL/images/dissemination/papers/Rotter2015_SoPh290_arxiv.pdf
import os

import cv2
import numpy as np
import urllib.request
import datetime
import global_config as k
import time
from decimal import Decimal, getcontext
import logging


# setup error logging
# logging levels in order of severity:
# DEBUG
# INFO
# WARNING
# ERROR
# CRITICAL
errorloglevel = logging.ERROR
logging.basicConfig(filename="errors.log", format='%(asctime)s %(message)s', level=errorloglevel)
filepath_sep = os.sep
getcontext().prec = 6


class SolarImageProcessor:
    def __init__(self, sun_url):
        self.coverage = 0
        self.sun_url = sun_url

    # ##############
    # M E T H O D S
    # ##############
    def _image_read(self, file_name):
        img = cv2.imread(file_name)
        return img

    def _image_write(self, file_name, image_name):
        cv2.imwrite(file_name, image_name)

    def _get_utc_time(self):
        # returns a STRING of the current UTC time
        time_now = str(datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        return time_now

    def _calc_histo(self, image_to_process):
        hist = cv2.calcHist([image_to_process], [0], None, [256], [0, 256])
        print(hist)

    def _greyscale_img(self, image_to_process):
        # converting an Image to grey scale...
        greyimg = cv2.cvtColor(image_to_process, cv2.COLOR_BGR2GRAY)
        return greyimg

    def _threshold_img(self, image_to_process):
        # Identify dark coronal hole areas from the solar surface...
        # This is crude at the moment, but it basically works
        # We will probably want to check the histogram for the image to define this
        # correctly. See original paper.
        ret, outputimg = cv2.threshold(image_to_process, 8, 255, cv2.THRESH_BINARY)
        return outputimg

    def _erode_dilate_img(self, image_to_process):
        # Erode and Dilate the image to clear up noise
        # Erosion will trim away pixels (noise)
        # dilation puffs out edges
        kernel = np.ones((5, 5), np.uint8)
        outputimg = cv2.erode(image_to_process, kernel, iterations=2)
        outputimg = cv2.dilate(outputimg, kernel, iterations=1)
        return outputimg

    def _mask_img(self, image_to_process, maskname):
        # Mask off the blowout due to the corona
        outputimg = cv2.bitwise_and(image_to_process, image_to_process, mask=maskname)
        return outputimg

    def _count_pixels(self, part_img, whole_img):
        # compare the ratio of pixels between two images to derive
        # the area occupied by coronal holes
        total_pixels = cv2.countNonZero(whole_img)
        remainder_pixels = cv2.countNonZero(part_img)
        coverage = 1 - (Decimal(remainder_pixels) / Decimal(total_pixels))
        return coverage

    def _make_mask(self, mask_filepath):
        mask = cv2.imread(mask_filepath, 0)
        return mask

    def _make_dynmask_segment(self, image):
        mask = np.zeros(image.shape[:2], dtype="uint8")
        dimensions = mask.shape
        width = dimensions[1]
        centre_x = int(width / 2)
        centre_y = int(width / 2)
        axis_long = int(width / 2 * 0.6)
        axis_short = int(width / 2 * 0.1)
        cv2.ellipse(mask, (centre_x, centre_x), (axis_short, axis_long), 0, 0, 360, (255, 255, 255), -1)
        return mask

    def _make_dynmask_full(self, image):
        mask = np.zeros(image.shape[:2], dtype="uint8")
        dimensions = mask.shape
        width = dimensions[1]
        radius = int(width / 2 * 0.6)
        centre_x = int(width / 2)
        centre_y = int(width / 2)
        cv2.circle(mask, (centre_x, centre_y), radius, (255, 255, 255), -1)
        return mask

    def _add_img_logo(self, image_name):
        dimensions = image_name.shape
        width = dimensions[1]

        label = 'DunedinAurora.NZ Coronal Hole Map'
        label2 = self._get_utc_time()
        # # SDO
        # cv2.putText(image_name, label, (10,482), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(250,250,250), 1 );
        # cv2.putText(image_name, label2, (10,498), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(250,250,250), 1 );
        # GOES
        cv2.putText(image_name, label, (10, int(width*0.031)), cv2.FONT_HERSHEY_SIMPLEX, (width*0.0014), (250, 250, 250), 2);
        cv2.putText(image_name, label2, (10, int(width*0.078)), cv2.FONT_HERSHEY_SIMPLEX, (width*0.0014), (250, 250, 250), 2);

        # cv2.imwrite('disc_full.bmp', image_name)
        return image_name

    def _add_ref_lines(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        dimensions = image.shape
        width = dimensions[1]
        print(width)

        band1 = int(width * 0.08)
        band2 = int(band1 * 2.1)
        radius1 = int(width * 0.29)
        radius2 = int(width * 0.25)

        centre_x = int(width / 2)

        cv2.line(image, (centre_x - radius2, centre_x + band2), (centre_x + radius2, centre_x + band2), (0, 124, 0), thickness=3)
        cv2.line(image, (centre_x - radius1, centre_x + band1), (centre_x + radius1, centre_x + band1), (0, 0, 255), thickness=5)
        cv2.line(image, (centre_x - radius1, centre_x - band1), (centre_x + radius1, centre_x - band1), (0, 0, 255), thickness=5)
        cv2.line(image, (centre_x - radius2, centre_x - band2), (centre_x + radius2, centre_x - band2), (0, 124, 0), thickness=3)

        axis_long = int(width / 2 * 0.6)
        axis_short = int(width / 2 * 0.1)
        cv2.ellipse(image, (centre_x, centre_x), (axis_short, axis_long), 0, 0, 360, (0, 0, 255), 3)

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_size = width * 0.00093
        font_thickness = int(width * 0.0015625)
        cv2.putText(image, "Weak", (centre_x - int(width*0.28), centre_x - band2 - int(width*0.15)), font,
                    font_size, (0, 124, 0),
                    font_thickness, cv2.LINE_AA)

        cv2.putText(image, "Effect", (centre_x - int(width*0.28), centre_x - band2 - int(width*0.12)), font,
                    font_size, (0, 124, 0),
                    font_thickness, cv2.LINE_AA)

        cv2.putText(image, "Mild", (centre_x - int(width*0.39), centre_x - band1 - int(width*0.054)), font,
                    font_size, (0, 124, 255),
                    font_thickness, cv2.LINE_AA)
        cv2.putText(image, "Effect", (centre_x - int(width*0.39), centre_x - band1 - int(width*0.023)), font,
                    font_size, (0, 124, 255),
                    font_thickness, cv2.LINE_AA)

        cv2.putText(image, "Strong", (centre_x - int(width*0.42), centre_x - int(width*0.015)), font,
                    font_size, (0, 0, 255),
                    font_thickness, cv2.LINE_AA)
        cv2.putText(image, "Effect", (centre_x - int(width*0.42), centre_x + int(width*0.015)), font,
                    font_size, (0, 0, 255),
                    font_thickness,cv2.LINE_AA)

        cv2.putText(image, "Mild", (centre_x - int(width*0.39), centre_x + band1 + int(width*0.039)), font,
                    font_size, (0, 124, 255),
                    font_thickness, cv2.LINE_AA)
        cv2.putText(image, "Effect", (centre_x - int(width*0.39), centre_x + band1 + int(width*0.07)), font,
                    font_size, (0, 124, 255),
                    font_thickness, cv2.LINE_AA)

        cv2.putText(image, "Weak", (centre_x - int(width*0.28), centre_x + band2 + int(width*0.12)), font,
                    font_size, (0, 124, 0),
                    font_thickness, cv2.LINE_AA)
        cv2.putText(image, "Effect", (centre_x - int(width*0.28), centre_x + band2 + int(width*0.15)), font,
                    font_size, (0, 124, 0),
                    font_thickness, cv2.LINE_AA)

        return image

    def _save_image_from_url(self, imageurl, filename):
        logging.debug("starting image from URL download: " + filename)
        try:
            request = urllib.request.Request(imageurl, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(request, timeout=10)
            with open(filename, 'wb') as f:
                f.write(response.read())
        except urllib.request.HTTPError:
            logging.error("Unable to load/save image from URL: " + str(imageurl) + " " + str(filename))

    # ################################
    # W R A P P E R   F U N C T I O N
    # ################################
    def get_meridian_coverage(self):
        if os.path.exists(k.stored_images_folder) is False:
            os.makedirs(k.stored_images_folder)

        try:
            self._save_image_from_url('https://services.swpc.noaa.gov/images/synoptic-map.jpg', 'syntopic.jpg')
        except:
            logging.debug("Unable to get syntopic map from NOAA")
            k.report_string = k.report_string + "Unable to get syntopic map from NOAA.\n"

        self._save_image_from_url(self.sun_url,"sun.jpg")
        img = self._image_read('sun.jpg')

        # Process the image to get B+W coronal hole image
        outputimg = self._greyscale_img(img)
        outputimg = self._threshold_img(outputimg)
        outputimg = self._erode_dilate_img(outputimg)

        mask_full = self._make_dynmask_full(img)
        mask_segment = self._make_dynmask_segment(img)

        # Full disk image
        outputimg1 = self._mask_img(outputimg, mask_full)


        # Start grabbing all processed images and save as jpg
        outputimg1 = self._add_img_logo(outputimg1)
        outputimg1 = self._add_ref_lines(outputimg1)

        try:
            time_now = str(datetime.datetime.utcnow().strftime("%Y_%m_%d_%H_%M"))
            filename = k.stored_images_folder + filepath_sep + time_now + ".jpg"
            # filename = "sun_jpegs/" + str(int(time.time())) + ".jpg"
            self._image_write(filename, outputimg1)
        except:
            logging.error("Unable to process running solar image in JPG folder")
            print("Unable to process running solar image in JPG folder")

        self._image_write('disc_full.jpg', outputimg1)

        # Meridian Segment
        outputimg2 = self._mask_img(outputimg, mask_segment)

        self._image_write('disc_segment.jpg', outputimg2)

        # Calculate the area occupied by coronal holes
        self.coverage = self._count_pixels(outputimg2, mask_segment)

        # It is extremely unlikely that we will ever get 100% coronal hole coverage on the meridian
        # Most ikely it is a glitched image from SDO - so we get less statistical grief if we reset the value
        # to a zero.
        if self.coverage == 1:
            self.coverage = 0

        # except:
        #     logging.error("Unable to process SDO image")
        #     common_data.report_string = common_data.report_string + "Unable to calculate coronal hole coverage.\n"
        #     self.coverage = 0

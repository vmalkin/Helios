import time
import re

import numpy as np
import requests
import os
import global_config
import standard_stuff
import cv2

def ring_system_bell():
    # rings the terminal bell.
    print("\a")

def add_stamp(image_object, utctime):
    cv2. rectangle(image_object, (0, 449), (511, 511), (255, 255, 255), -1)
    cv2.rectangle(image_object, (0, 0), (511, 20), (255, 255, 255), -1)
    colour = (0, 0, 0)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_size = 0.5
    font_color = colour
    font_thickness = 1
    banner = "Processed at " + global_config.copyright
    x, y = 5, 15
    cv2.putText(image_object, banner, (x, y), font, font_size, font_color, font_thickness, cv2.LINE_AA)
    banner = 'LASCO coronagraph. Updated ' + utctime + " UTC."
    x, y = 5, 466
    cv2.putText(image_object, banner, (x, y), font, font_size, font_color, font_thickness, cv2.LINE_AA)

    banner = 'Courtesy of SOHO/LASCO consortium. SOHO is a project of'
    x, y = 5, 492
    cv2.putText(image_object, banner, (x, y), font, font_size, font_color, font_thickness, cv2.LINE_AA)
    banner = 'international cooperation between ESA and NASA'
    x, y = 5, 508
    cv2.putText(image_object, banner, (x, y), font, font_size, font_color, font_thickness, cv2.LINE_AA)

def get_resource_from_url(url_to_get):
    response = ""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url_to_get, headers=headers)
    except:
        print("unable to load URL", url_to_get)
        print("Try: pip install --upgrade certifi")
    return response

def parseimages(listofimages, imagestore):
    # Identifies if any images in the listofimages currently exist. If so they are removed from the list
    # and the revised list is returned.
    set_downloads = set(listofimages)
    stored = os.listdir(imagestore)
    set_stored = set(stored)
    newfiles = set_downloads.difference(set_stored)
    return newfiles

def downloadimages(listofimages, storagelocation):
    for img in listofimages:
        file = storagelocation + os.sep + img
        i = img.split(".")
        baddy = str(i[0])
        badfile = storagelocation + os.sep + baddy + ".no"
        img1url = baseURL + img
        if not os.path.exists(badfile):
            if not os.path.exists(file):
                response1 = get_resource_from_url(img1url)
                print("Saving file ", file)
                with open(file, 'wb') as f:
                    f.write(response1.content)
                f.close()
        else:
            print("Corrupted image bypassed from processing")

def get_imagelist(url_to_get):
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url_to_get, headers=headers)
    r = r.text.split("\n")
    #  The response is now delimited on newlines. We can get rid lines to only have the HTML with the images
    # Remove the content above and below the table that contains images
    r = r[13:]
    r = r[:-4]
    # Now split the lines around image file names. Return only the ones 512 in size
    returnlist = []
    for line in r:
        l1 = line.split("href=\"")
        if len(l1) == 2:
            l2 = (l1[1])
            l2 = l2.split("\"")
            filename = l2[0]
            # if re.search("c3_1024", filename):
            if re.search("c3_512", filename):
                returnlist.append(filename)
    return returnlist

def download_lasco(lasco_url, storage_folder):
    print(lasco_url)
    listofimages = get_imagelist(lasco_url)
    newimages = parseimages(listofimages, storage_folder)
    if len(newimages) > 0:
        ring_system_bell()
        downloadimages(newimages, storage_folder)


if __name__ == "__main__":
    # Define the beginning of the current computation, and the start date of images we want to process.
    computation_start = time.time()
    processing_start_date = int(computation_start - (86400 * 1))

    # If necessary, create the storage folder for lasco images. Otherwise, download latest images.
    storage_folder = global_config.folder_source_images + os.sep + "store_lasco_512"
    if not os.path.exists(storage_folder):
        os.makedirs(storage_folder)

    tm = int(computation_start)
    ymd_now = int(standard_stuff.posix2utc(tm, "%Y%m%d"))
    ymd_old = ymd_now - 3
    year = standard_stuff.posix2utc(tm, "%Y")

    for epoch in range(ymd_now, ymd_old, - 1):
        # LASCO coronagraph
        baseURL = "https://soho.nascom.nasa.gov/data/REPROCESSING/Completed/" + year + "/c3/" + str(epoch) + "/"
        download_lasco(baseURL, storage_folder)

    # #####################################################################################################
    # Processing and analysis of LASCO images happens here
    # #####################################################################################################
    enhanced_folder = global_config.folder_source_images + os.sep + "enhanced_lasco"
    analysis_folder = global_config.folder_source_images + os.sep + "analysis_lasco"

    if not os.path.exists(enhanced_folder):
        os.makedirs(enhanced_folder)
    if not os.path.exists(analysis_folder):
        os.makedirs(analysis_folder)

    # BEGIN enhancesment of LASCO images, removing particle strikes and improve contrast.
    # Generate file list of current lasco images for the past 24 hours or other time.
    file_list = os.listdir(storage_folder)
    file_list.sort()
    # The array item in list of current files has the format [posixtimestamp, filename]
    current_files = []
    for f in file_list:
        ff = f.split("_")
        timestamp = ff[0] + ff[1]
        file_posix_time = standard_stuff.utc2posix(timestamp, '%Y%m%d%H%M')
        # If the file timestamp is within our time interval
        if file_posix_time >= processing_start_date:
            dp = [file_posix_time, f]
            current_files.append(dp)
    # Remove particle hits by taking the rolling median of 3 images, provided there is no time interval between any
    # image greater than some empirically determined value. Create an array of new images from this.
    time_threshold = 60 * 120
    # The cleaned mage array stores [posixtimestamp, processed_image_binary]
    cleaned_picture_array = []
    filepath = storage_folder +  os.sep
    if len(current_files) > 3:
        for i in range(1, len(current_files) - 1):
            temp_images = [current_files[i - 1], current_files[i], current_files[i + 1]]
            a = np.array(temp_images, dtype=object)
            tmp_times = a[:, 0]
            tmp_images = a[:, 1]
            if max(tmp_times) - min(tmp_times) <= time_threshold:
                # load images and create new image based on median values
                img_1 = cv2.imread(filepath + tmp_images[0], 0)
                img_2 = cv2.imread(filepath + tmp_images[1], 0)
                img_3 = cv2.imread(filepath + tmp_images[2], 0)
                t = [img_1, img_2, img_3]
                median_filtered_image = np.median(t, axis=0)
                psx_timestamp = tmp_times[1]
                dp = [psx_timestamp, median_filtered_image]
                cleaned_picture_array.append(dp)

    # If everything works out, apply image contrast/enhancement to median image array
    processed_images = []
    for item in cleaned_picture_array:
        psx_timestamp = item[0]
        median_image = item[1]

        # alpha value [1.0-3.0] CONTRAST
        # beta value [0-100] BRIGHTNESS
        alpha = 1.5
        beta = 2
        picture = cv2.convertScaleAbs(median_image, alpha=alpha, beta=beta)
        clahe = cv2.createCLAHE(clipLimit=2, tileGridSize=(10, 10))
        picture = clahe.apply(picture)
        picture = cv2.applyColorMap(picture, cv2.COLORMAP_OCEAN)
        dp = [psx_timestamp, picture]
        processed_images.append(dp)

    # This array can be passed to a local analyser to automatically calculate if a possible CME has been detected
    # This creates a new set of images that have been convoluted and saved in the analysis folder.

    # Add Dunedin Aurora stamp to images in array
    # Write out images to files. FINISHED!
    for item in processed_images:
        psx_timestamp = item[0]
        img_data = item[1]
        filename = standard_stuff.posix2utc(psx_timestamp, '%Y%m%d_%H%M')
        savefile = enhanced_folder + os.sep + str(filename) + ".png"
        add_stamp(img_data, utctime=filename)
        cv2.imwrite(savefile, img_data)

    # #####################################################################################################
    # End of LASCO download and analysis
    # #####################################################################################################

    # FINAL HOUSEKEEPING - prune the size of the LASCO storage folder to some sane value. Perhaps the last 7 or 14 days?

    computation_end = time.time()
    elapsed_mins = round((computation_end - computation_start) / 60, 1)
    print(f"Processing time is {elapsed_mins} minutes")

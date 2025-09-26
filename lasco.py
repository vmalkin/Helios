import time
import re
import requests
import os
import global_config
import standard_stuff

def ring_system_bell():
    # rings the terminal bell.
    print("\a")

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
    computation_start = time.time()
    # If necessary, create the storage folder for lasco images. Otherwise, download latest images.
    storage_folder = global_config.folder_source_images + os.sep + "store_lasco_512"
    if not os.path.exists(storage_folder):
        os.makedirs(storage_folder)

    tm = int(time.time())
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
    processing_start_date = int(time.time() - (86400 * 1))
    if not os.path.exists(enhanced_folder):
        os.makedirs(enhanced_folder)
    if not os.path.exists(analysis_folder):
        os.makedirs(analysis_folder)
    # BEGIN enhancesment of LASCO images, removing particle strikes and improve contrast.
    # Generate file list of current lasco images for the past 24 hours or other time interval

    # Remove particle hits by taking the rolling median of 3 images, provided there is no time interval between any
    # image greater than some empirically determined value. CReate a new image from this.

    # If everything works out, apply image contrast/emhancement

    # At this point we can apply the local analyser to automatically calculate if a possible CME has been detected
    # This creates a new set of images that have been convoluted and saved in the analysis folder.

    # Add Dunedin Aurora stamp to image.
    # Save image - FINISHED

    # #####################################################################################################
    # End of LASCO download and analysis
    # #####################################################################################################
    computation_end = time.time()
    elapsed_mins = round((computation_end - computation_start) / 60, 1)
    print(f"Processing time is {elapsed_mins} minutes")

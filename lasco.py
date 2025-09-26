import time
import re
import requests
import os
import global_config
import standard_stuff


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
                    # f.write(response1.read())
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
        # rings the terminal bell
        print("\a")
        downloadimages(newimages, storage_folder)


if __name__ == "__main__":
    computation_start = time.time()
    # If necessary, create the storage folder for lasco images. Otherwise, download latest images.
    storage_folder = global_config.folder_source_images + os.sep + "store_lasco_512"
    if not os.path.exists(storage_folder):
        os.makedirs(storage_folder)

    tm = int(time.time())
    ymd_now = int(standard_stuff.posix2utc(tm, "%Y%m%d"))
    ymd_old1 = ymd_now - 1
    ymd_old2 = ymd_old1 - 1
    year = standard_stuff.posix2utc(tm, "%Y")

    # LASCO coronagraph
    baseURL = "https://soho.nascom.nasa.gov/data/REPROCESSING/Completed/" + year + "/c3/" + str(ymd_now) + "/"
    download_lasco(baseURL, storage_folder)

    # Parse for old epoch files that have been added
    baseURL = "https://soho.nascom.nasa.gov/data/REPROCESSING/Completed/" + year + "/c3/" + str(ymd_old1) + "/"
    download_lasco(baseURL, storage_folder)

    # Parse for old epoch files that have been added
    baseURL = "https://soho.nascom.nasa.gov/data/REPROCESSING/Completed/" + year + "/c3/" + str(ymd_old2) + "/"
    download_lasco(baseURL, storage_folder)

    # #####################################################################################################
    # Processing and analysis of LASCO images happens here
    # #####################################################################################################


    # #####################################################################################################
    # End of LASCO download an analysis
    # #####################################################################################################
    computation_end = time.time()
    elapsed_mins = round((computation_end - computation_start) / 60, 1)
    print(f"Processing time is {elapsed_mins} minutes")

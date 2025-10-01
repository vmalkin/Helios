import glob
import requests
import os
import global_config

goes_dict = global_config.goes_dict

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


def get_resource_from_url(url_to_get):
    response = ""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url_to_get, headers=headers)
    except:
        print('unable to load URL', url_to_get)
        print('Try: pip install --upgrade certifi')
    return response


def parseimages(listofimages, imagestore):
    set_downloads = set(listofimages)
    stored = os.listdir(imagestore)
    set_stored = set(stored)
    newfiles = set_downloads.difference(set_stored)
    return newfiles


def downloadimages(img_url, listofimages, storagelocation):
    for img in listofimages:
        file = storagelocation + pathsep + img
        img1url = img_url + img
        # print(file, img1url)
        if os.path.exists(file) is False:
            response1 = get_resource_from_url(img1url)
            print('Saving file ', file)
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

    r = r[9:]
    r = r[:-3]

    # Now split the lines around image file names. Return only the ones 512 in size
    returnlist = []
    for line in r:
        l = line.split('href=')
        l1 = l[1].split('>or_suvi')
        f = l1[0][1:-1]
        # print(f)
        returnlist.append(f)
    return returnlist


def playbell():
    # Ring the system bell
    pass


def download_suvi(lasco_url, storage_folder):
    print(lasco_url)
    listofimages = get_imagelist(lasco_url)
    newimages = parseimages(listofimages, storage_folder)
    if len(newimages) > 0:
        # rings the terminal bell
        print("\a")
        playbell()
        downloadimages(lasco_url, newimages, storage_folder)


if __name__ == '__main__':
    # Check for save folders
    for sat in goes_dict:
        if not os.path.exists(goes_dict[sat]['false_colour']):
            os.makedirs(goes_dict[sat]['false_colour'])

        if not os.path.exists(goes_dict[sat]['false_diffs']):
            os.makedirs(goes_dict[sat]['false_diffs'])

    for sat in goes_dict:
        for key in goes_dict[sat]['wavelengths']:
            if not os.path.exists(goes_dict[sat]['wavelengths'][key]['store']):
                os.makedirs(goes_dict[sat]['wavelengths'][key]['store'])

            if not os.path.exists(goes_dict[sat]['wavelengths'][key]['diffs']):
                os.makedirs(goes_dict[sat]['wavelengths'][key]['diffs'])

    if not os.path.exists(global_config.folder_output_to_publish):
        os.makedirs(global_config.folder_output_to_publish)

    # get the latest SUVI images
    for sat in goes_dict:
        for key in goes_dict[sat]['wavelengths']:
            url = goes_dict[sat]['wavelengths'][key]['url']
            savepath = goes_dict[sat]['wavelengths'][key]['store']
            download_suvi(url, savepath)

    print("*** All image downloading COMPLETED")

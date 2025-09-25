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
        goes_data = global_config.goes_dict
        for sat in goes_data:
                sat_name = sat
                for key in goes_data[sat]['wavelengths']:
                        # print(goes_dict[sat]['wavelengths'][key]['url'])
                        print(key)
                        print(goes_data[sat]['wavelengths'][key]['diffs'])
                        satname = sat
                        wavelength = key
                        diffs = goes_data[sat]['wavelengths'][key]['diffs']
                        store = goes_data[sat]['wavelengths'][key]['store']

                        img_files = local_file_list_build(store)
                        diff_files = local_file_list_build(diffs)

                        # a day is roughly 360 images
                        img_files = img_files[-360:]
                        diff_files = diff_files[-360:]
                        img_movie = satname + "_" +wavelength + "_" + "img"
                        diff_movie = satname + "_" +wavelength + "_" + "diff"
                        imgfile = global_config.folder_output_to_publish + os.sep + img_movie
                        difffile = global_config.folder_output_to_publish + os.sep + diff_movie
                        make_anim.wrapper(img_files, imgfile)
                        make_anim.wrapper(diff_files, difffile)

        for sat in goes_data:
            sat_name = sat
            fc_images = goes_data[sat]['false_colour']
            fc_diffs = goes_data[sat]['false_diffs']

            # a day is roughly 360 images
            fc_files = local_file_list_build(fc_images)
            fc_files = fc_files[-360:]
            diff_files = local_file_list_build(fc_diffs)
            diff_files = diff_files[-360:]

            fc_output = global_config.folder_output_to_publish + os.sep + sat + '_3_clr'
            fc_df_output = global_config.folder_output_to_publish + os.sep + sat + '_3_clr_df'
            make_anim.wrapper(fc_files, fc_output)
            make_anim.wrapper(diff_files, fc_df_output)

        folder = global_config.folder_source_images + os.sep + 'enhanced_lasco'
        img_files = local_file_list_build(folder)
        # a day is roughly 360 images
        img_files = img_files[-360:]
        outputfile = global_config.folder_output_to_publish + os.sep + 'lasco'
        make_anim.wrapper(img_files, outputfile)
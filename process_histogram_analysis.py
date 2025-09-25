import glob
import os
import cv2
import numpy as np
from plotly import graph_objects as go
import global_config


# file path seperator / or \ ???
pathsep = os.sep


def create_mask(image):
    # Mask off the outer corona and only focus on the image of the sun
    diameter_ratio = 400 / 1280
    width, height, colourdepth = image.shape
    solar_diameter = int(diameter_ratio * width)
    mask = np.zeros((width, height), dtype=np.int8)
    x_offset = 0
    y_offset = 0
    x_centre = int(width / 2) + x_offset
    y_centre = int(height / 2) + y_offset
    cv2.circle(mask, (x_centre, y_centre), solar_diameter, (255,255,255), -1)
    image = cv2.bitwise_and(image, image, mask=mask)
    return image


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


def getfilename(pathname):
    p = pathname.split(pathsep)
    pp = p[2].split('_')
    return pp[0]


def plot(event_data, sat_name):
    fig = go.Figure()
    papercolour = "#e0e0e0"
    gridcolour = "#c0c0c0"
    bar_fill = ['#f57600','#fcec0e','#19aecf']
    width = 1500
    height = 500

    max_y = 10
    for i in range(0, len(event_data)):
        # Each data is is an array [datetime, data1, data2]
        dt = []
        d0 = []
        d1 = []
        for entries in event_data[i]:
            dt.append(entries[0])
            d0.append(entries[1])
            d1.append(entries[2])

        fig.add_bar(x=dt, y=d0, width=0.7, marker_color=bar_fill[i], marker_line_color='black', marker_line_width=0.5)
        fig.add_bar(x=dt, y=d1, width=0.7, marker_color=bar_fill[i], marker_line_color='black', marker_line_width=0.5)

    # Force y axis to show at least 10
    fig.update_layout(bargap=0)
    fig.update_yaxes(range=[0, 20])
    fig.update_xaxes(tickangle=45, dtick=20, showgrid=True,)
    fig.update_layout(barmode='group')

    title = "Solar Surface Event Occurrences: " + sat_name
    fig.update_layout(width=width, height=height, title=title,
                      xaxis_title="UTC Datetime<br><sub>" + global_config.copyright + " http://DunedinAurora.nz</sub>")
    fig.update_layout(yaxis_title="Px Count - Sigmas")
    fig.update_layout(font=dict(size=16, color="#202020"), title_font_size=18, )
    fig.update_layout(plot_bgcolor=papercolour, paper_bgcolor=papercolour)
    file_html = global_config.folder_output_to_publish + os.sep +  sat_name + '_hist.html'
    file_png = global_config.folder_output_to_publish + os.sep + sat_name + '_hist.png'
    fig.write_html(file_html)
    fig.write_image(file_png)

if __name__ == '__main__':
    print('*** Begin Histogram Analysis')

    # Supply a list of sub folders with diffs images in them to analyse
    goes_dict = global_config.goes_dict
    for sat in goes_dict:
        solar_surface_events = []
        for key in goes_dict[sat]['wavelengths']:
            diffs = goes_dict[sat]['wavelengths'][key]['diffs']
            img_files = local_file_list_build(diffs)
            # a day is roughly 360 images
            img_files = img_files[-360:]

            returnarray = []
            for item in img_files:
                tmp = []
                img = cv2.imread(item)
                # Mask off the outer corona - we're only interested in the solar disc
                img = create_mask(img)
                # CReate a histogram of the image being processed
                result = np.histogram(img, bins=5, range=(0, 256))
                # result[0] is histogram, result[1] are bin labels
                histgm = (result[0])
                tmp.append(getfilename(item))
                tmp.append(histgm[0])
                tmp.append(histgm[4])
                returnarray.append(tmp)

            px_white = []
            px_black = []
            dates = []
            for item in returnarray:
                dates.append(item[0])
                px_white.append(item[1])
                px_black.append(item[2])

            # Get simple statistics of the average, and standard deviations for all-black and all-white
            # pixels for the current 24 hour period. Use this to determine of any single image is above average, this will
            # be our simple indicator of rapid change in the image caused by CME or similar events on the sun's surface
            # It is possible that we might need a better treatment of this? We might want to store STD and AVG over
            # a period of time and use the median values of those to evaluate individual images?
            avg_white = np.average(px_white)
            std_white = np.std(px_white)
            avg_black = np.average(px_black)
            std_black = np.std(px_black)

            #
            events = []
            for i in range(0, len(dates)):
                dt = dates[i]

                # White pixel count in Sigmas, if the pixel count is over 1 Sigma
                if px_white[i] > (avg_white + std_white):
                    cme_wh = round(((px_white[i] - avg_white) / std_white), 3)
                else:
                    cme_wh = 0

                # Black pixel count in Sigmas, if the pixel count is over 1 Sigma
                if px_black[i] > (avg_black + std_black):
                    cme_bl = round(((px_black[i] - avg_black) / std_black), 3)
                else:
                    cme_bl = 0

                line = [dt, cme_wh, cme_bl]
                events.append(line)
            solar_surface_events.append(events)

        plot(solar_surface_events, sat)
    print('*** End Histogram Analysis')

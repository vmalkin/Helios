import os
import cv2
import numpy as np
from math import sin, cos, radians
import datetime
import time
import calendar
from plotly import graph_objects as go
import glob
import global_config

# offset values when coronagraph mask support-vane in top-right position
# offset_x = -4
# offset_y = 10

# offset values when coronagraph mask support-vane in bottom-left position
offset_x = 4
offset_y = -10

image_size = 512
imagecentre = image_size / 2

# Parameters for CME detection
cme_min = 0.4
cme_partial = 0.5
cme_halo = 0.8


def process_columns(image):
# takes a cropped image. Determins a value for each column in the image.
# A CME should appear as a surge in brighness across several connected columns that
# changes with time.
# Streamers are ever present, but although contiguous, change far more slowly
    returnarray = []
    img = np.array(image)
    array_length = image.shape[1]
    for i in range(0, array_length):
        column_sum = sum(img[:,i])
        returnarray.append(column_sum)
    return returnarray


def plot_diffs_polar(pixel_count, filename, width, height):
    savefile = global_config.folder_output_to_publish + os.sep + filename
    colourstep = 255 / len(pixel_count)
    papercolour = "#303030"

    theta = []
    for i in range(0, len(pixel_count[0])):
        j = i / len(pixel_count[0]) * 360
        theta.append(j)
    theta.append(0)

    x_step = -0.02
    x1_step = 0.00
    fig = go.Figure()
    for i in range(0, len(pixel_count)):
        j = int(colourstep * i)
        linecolour = "rgba(" + str(j) + ", 0," + str(255 - j) + ", 1)"
        fig.add_shape(type="rect", xref="paper", yref="paper", x0=x_step, y0=-0.04, x1=x1_step, y1=-0.02,
                      line=dict(color=linecolour),
                      fillcolor=linecolour)
        fig.add_trace(go.Scatterpolar(
            r=pixel_count[i],
            theta=theta,
            mode="lines",
            line_color=linecolour))

        if i == len(pixel_count) - 1:
            fig.add_shape(type="rect", xref="paper", yref="paper", x0=x_step, y0=-0.04, x1=x1_step, y1=-0.02,
                          line=dict(color="yellow"),
                          fillcolor="yellow")
            fig.add_trace(go.Scatterpolar(
                r=pixel_count[i],
                theta=theta,
                mode="lines",
                line_color="#ffff00"))
        x_step = x_step + 0.009
        x1_step = x1_step + 0.009

    # The Sun
    sun_x = int(width / 2) - 80
    sun_y = int(height / 2) - 90
    fig.add_shape(
        type="circle",
        # xref="x", yref="y",
        xsizemode="pixel", ysizemode="pixel",
        xanchor=0, yanchor=0,
        x0=sun_x - 50, y0=sun_y - 50,
        x1=sun_x + 50, y1=sun_y + 50,
        fillcolor="gold")

    fig.update_layout(font=dict(size=20, color="#e0e0e0"), title_font_size=21)
    fig.update_layout(paper_bgcolor=papercolour)
    fig.update_layout(showlegend=False, width=width, height=height,
                      title="Solar Corona - 24 Hrs - Brightness and Azimuth")

    fig.add_annotation(text="24 Hours ago", x=0.1, y=-0.03)
    fig.add_annotation(text="NOW", x=1.03, y=-0.03)

    fig.update_polars(
        hole=0.2,
        bgcolor="#000000",
        angularaxis_linecolor=papercolour,
        angularaxis_direction="clockwise",
        angularaxis_rotation=90,
        angularaxis_gridwidth=4,
        angularaxis_gridcolor=papercolour,
        radialaxis_gridwidth=4,
        radialaxis_gridcolor=papercolour,
        radialaxis_showticklabels=True,
        radialaxis_color="white",
        radialaxis_linewidth=3,
        radialaxis=dict(angle=90),
        radialaxis_tickangle=90
    )
    fig.write_image(file=savefile, format='jpg')


def plot(dates, pixel_count, filename, width, height):
    savefile = global_config.folder_output_to_publish + os.sep + filename
    # pixel_count = median_filter(pixel_count)
    dates.pop(0)
    dates.pop(len(dates) - 1)
    red = "rgba(150, 0, 0, 1)"
    green = "rgba(0, 150, 0, 0.8)"
    orange = "rgba(200, 100, 0, 0.8)"

    plotdata = go.Scatter(x=dates, y=pixel_count, mode="lines")
    fig = go.Figure(plotdata)

    fig.update_layout(font=dict(size=20), title_font_size=21)
    fig.update_layout(width=width, height=height, title="Total Coronal Brightness @ 3 Solar diameters",
                      xaxis_title="Date/time UTC<br><sub>" + global_config.copyright + " http://DunedinAurora.nz</sub>",
                      yaxis_title="Brightness 0 -  1",
                      plot_bgcolor="#e0e0e0")
    fig.update_layout(plot_bgcolor="#a0a0a0", paper_bgcolor="#a0a0a0")

    fig.update_xaxes(nticks=12, tickangle=45)

    # fig.add_hline(y=cme_min, line_color=green, line_width=6, annotation_text=cme_min,
    #               annotation_font_color=green, annotation_font_size=20, annotation_position="top left")

    # fig.add_hline(y=cme_partial, line_color=orange, line_width=6, annotation_text="50%",
    #               annotation_font_color=orange, annotation_font_size=20, annotation_position="top left")
    #
    # fig.add_hline(y=cme_halo, line_color=red, line_width=6, annotation_text="80%",
    #               annotation_font_color=red, annotation_font_size=20, annotation_position="top left")

    fig.update_traces(line=dict(width=8, color=red))
    fig.write_image(file=savefile, format='jpg')


def annotate_image(array, width, height, timevalue):
    #  downconvert image
    cimage = np.array(array, np.uint16)
    cimage = cv2.cvtColor(cimage, cv2.COLOR_GRAY2BGR)

    rad_sol = 10  # solar radius in pixels at 512 pixels
    north = 0
    east = 90
    south = 180
    west = 270

    # NSWE lines
    cv2.line(cimage, (north, 0), (north, height), (0, 100, 255), thickness=1)
    cv2.line(cimage, (east, 0), (east, height), (0, 100, 255), thickness=1)
    cv2.line(cimage, (south, 0), (south, height), (0, 100, 255), thickness=1)
    cv2.line(cimage, (west, 0), (west, height), (0, 100, 255), thickness=1)
    # solar surface
    cv2. rectangle(cimage, (0, height - rad_sol), (width, height), (0, 255, 255), -1)
    cv2.rectangle(cimage, (0, 0), (width, 12), (0, 0, 0), -1)

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_size = 0.4
    font_color = (0, 100, 255)
    font_thickness = 1
    cv2.putText(cimage, "N", (north, 10), font, font_size, font_color, font_thickness, cv2.LINE_AA)
    cv2.putText(cimage, "E", (east, 10), font, font_size, font_color, font_thickness, cv2.LINE_AA)
    cv2.putText(cimage, "S", (south, 10), font, font_size, font_color, font_thickness, cv2.LINE_AA)
    cv2.putText(cimage, "W", (west, 10), font, font_size, font_color, font_thickness, cv2.LINE_AA)

    font_color = (0, 255, 255)
    cv2.putText(cimage, "Solar Surface", (10, height - 15), font, font_size, font_color, font_thickness, cv2.LINE_AA)
    cv2.putText(cimage, timevalue, (220, height - 15), font, font_size, font_color, font_thickness, cv2.LINE_AA)
    # THis box marks the slot used to detect count pixels for CMEs
    cv2.rectangle(cimage, (0, 220 - 50), (359, 220 - 40), (0, 255, 0), 1)
    return cimage


def text_alert(px, hr):
    # %Y-%m-%d %H:%M
    cme_detect = False
    timestring = hr
    hr = hr.split(" ")
    hr = hr[0]
    hr = hr.split("-")
    new_hr = hr[0] + "/" + hr[1] + "/" + hr[2]
    url = "https://stereo-ssc.nascom.nasa.gov/browse/" + new_hr +  "/ahead/cor2_rdiff/512/thumbnail.shtml"
    stereo_url = "<a href=\"" + url + "\" target=\"_blank\">" + "Stereo Science Centre</a>"
    savefile = global_config.folder_output_to_publish + os.sep + "cme_alert.php"
    heading = "<b>CME Monitor updated at " + posix2utc(time.time(), " %Y-%m-%d %H:%M") + " UTC.</b>"
    msg = "<p>Highest level of coronal brightness occurred " + timestring +  " with " + str(int(px * 100)) + "% coverage."
    msg = msg + "<p>Latest STEREO A images can be found at:<br>"
    # if cme_detect == True:
    #     msg = msg + "<br>Confirm Earth impact with STEREO A satellite data: "
    msg_alert = heading + msg + stereo_url
    with open(savefile, "w") as s:
        s.write(msg_alert)
    s.close()


def filehour_converter(yyyymmdd, hhmm):
    year = (yyyymmdd[:4])
    month = (yyyymmdd[4:6])
    day = (yyyymmdd[6:])
    hour = (hhmm[:2])
    min = (hhmm[2:])
    utc_string = year + '-' + month + '-' + day + ' ' + hour + ':' + min
    dt = datetime.datetime.strptime(utc_string, '%Y-%m-%d %H:%M')
    ts = calendar.timegm(dt.timetuple())
    return ts


def posix2utc(posixtime, timeformat):
    # '%Y-%m-%d %H:%M'
    utctime = datetime.datetime.utcfromtimestamp(int(posixtime)).strftime(timeformat)
    return utctime


def crop_image(image, imagewidth, imageheight, topoffset, bottomoffset):
    cropped_img = image[imageheight - bottomoffset:imageheight - topoffset, 0:imagewidth]
    # print(cropped_img)
    return cropped_img


def polar_to_rectangular(angle, distance):
    """
    With our image, we have a line at an angle , radiating from
    the centre. We want the pixel value at the end. THis method will return the [x,y] co-ords accounting
    for the offset the actual centre point from the geometric centre of the image

    Angle: in degrees measured clockwise from North/top
    Distance: in pixels, as a radius measured from the centre.
    """
    if angle == 0 or angle == 360:
        # print("a == 0")
        x = imagecentre
        y = imagecentre - distance

    if angle > 0:
        if angle < 90:
            # print("0 < a < 90")
            delta_x = distance * sin(radians(angle))
            delta_y = distance * cos(radians(angle))
            x = imagecentre + delta_x
            y = imagecentre - delta_y

    if angle == 90:
        # print("a == 90")
        x = imagecentre + distance
        y = imagecentre

    if angle > 90:
        if angle < 180:
            # print("90 < a < 180")
            angle = angle - 90
            delta_y = distance * sin(radians(angle))
            delta_x = distance * cos(radians(angle))
            x = imagecentre + delta_x
            y = imagecentre + delta_y

    if angle == 180:
        # print("a == 180")
        x = imagecentre
        y = imagecentre + distance

    if angle > 180:
        if angle < 270:
            # print("180 < a < 270")
            angle = angle - 180
            delta_x = distance * sin(radians(angle))
            delta_y = distance * cos(radians(angle))
            x = imagecentre - delta_x
            y = imagecentre + delta_y

    if angle == 270:
        # print("a == 270")
        x = imagecentre - distance
        y = imagecentre

    if angle > 270:
        if angle < 360:
            # print("270 < a < 360")
            angle = angle - 270
            delta_y = distance * sin(radians(angle))
            delta_x = distance * cos(radians(angle))
            x = imagecentre - delta_x
            y = imagecentre - delta_y

    # finally add the offsets and return
    x = int(x + offset_x)
    y = int(y + offset_y)
    return [x, y]


def image_save(file_name, image_object):
    cv2.imwrite(file_name, image_object)


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
        returnstring = utc_string
    elif switch == "filename":
        returnstring = filename
    else:
        returnstring = calendar.timegm(dt.timetuple())
    # return posix by default
    return returnstring


def shorten_dirlisting(directory_listing):
    returnarray = directory_listing[-360:]
    return returnarray


def median_image(img_1, img_2, img_3):
    try:
        t = [img_1, img_2, img_3]
        p = np.median(t, axis=0)
    except:
        print('Unable to apply median filter to images')
        p = None
    return p


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


def wrapper(lasco_folder, analysis_folder):
    print("*** Analyser: Start")
    # get a list of the current stored images.
    # IGNORE files with the suffix .no as they are corrupted or reconstructed by the LASCO team, and the
    # interpolated data in inaccurate

    # Used in the convolving of the image among other things
    radius = 220
    angle = 360

    dirlisting = local_file_list_build(lasco_folder)

     # We do not need ALL of the images in the Lasco folder, only the last day or so. Approx
    dirlisting = shorten_dirlisting(dirlisting)

    avg_array = []
    cme_count = []
    cme_spread = []
    dates = []
    lasco_array = []

    # Add images to lasco array
    for i in range (0, len(dirlisting)):
        p = dirlisting[i]
        # load images into the lasco array
        lasco_array.append(cv2.imread(p, 0))

    print("*** Analyser: Remove visual static")
    # Calculate and store the median image thus removing visual static
    # Apply any enhancements as well
    median_pictures = []
    for i in range(1, len(lasco_array) - 1):
        picture = median_image(lasco_array[i - 1], lasco_array[i], lasco_array[i + 1])
        if picture is not None:
            # alpha value [1.0-3.0] CONTRAST
            # beta value [0-100] BRIGHTNESS
            alpha = 1.5
            beta = 2
            picture = cv2.convertScaleAbs(picture, alpha=alpha, beta=beta)
            clahe = cv2.createCLAHE(clipLimit=2, tileGridSize=(10, 10))
            picture = clahe.apply(picture)
            median_pictures.append(picture)

    print("*** Analyser: Convolving images")
    # convolve the median images
    convolved_images = []
    for image_m in median_pictures:
        #  convolve the returned residuals image from polar to rectangular co-ords. the data is appended to
        #  an array
        pic_new = np.zeros([radius, angle])
        for j in range(0, radius):
            for k in range(0, angle):
                coords = polar_to_rectangular(k, j)
                pic_new[j][k] = image_m[coords[1], coords[0]]
            # Convert the 1D array into a 2D image.
            pic_new = np.reshape(pic_new, (radius, angle))
        pic_new = cv2.flip(pic_new, 0)
        convolved_images.append(pic_new)

    # Fix dirlisting to have the correct length. Save annotated file to analysis folder
    dirlisting.pop(len(dirlisting) - 1)
    dirlisting.pop(0)
    for i in range(0, len(convolved_images)):
        d = dirlisting[i].split(os.sep)
        dd = d[2]
        dt = filename_converter(dd, "utc")
        savefile = analysis_folder + os.sep + dd
        img = annotate_image(convolved_images[i], angle, radius, dt)
        cv2.imwrite(savefile, img)

    print("*** Analyser: Creating cropped image for analysis")
    # Create the cropped image for CME analysis
    cropped_image = []
    for img in convolved_images:
        new_img = crop_image(img, angle, radius, 40, 50)
        cropped_image.append(new_img)

    # datelist for plotting
    datelist = []
    for item in dirlisting:
        i = item.split(os.sep)
        ii = i[2]
        datelist.append(filename_converter(ii, "utc"))

    print("*** Analyser: Calculating general brightness of corona")
    # calculate the general brightness of the corona near the sun
    brightness = []
    for i in range(1, len(cropped_image) - 1):
        a = np.array(cropped_image[i])
        value = np.sum(a) / (360 * 10 * 254)
        brightness.append(value)

    print("*** Analyser: Calculating radial cordinates of coronal hotspots")
    # analyse the cropped image for where cme brightness occurs.
    # This becomes a polar plot of the sun's coronal brightness
    stacked_brightness = []
    for item in cropped_image:
        summed_cols = process_columns(item)
        stacked_brightness.append(summed_cols)

    print("*** Analyser: Generating plots")
    plot(datelist, brightness, "corona_value.jpg", 1000, 600)
    plot_diffs_polar(stacked_brightness, "cme_polar.jpg", 800, 950)

    print("*** Analyser: Creating alert and STEREO A confirmation link")
    # If the max value of the detrended data is over 0.5 then we can write an alert for potential
    # CMEs to check.
    px = max(brightness)
    print(px)
    hr = datelist[brightness.index(max(brightness))]
    text_alert(px, hr)
    print("*** Analyser: Finished")

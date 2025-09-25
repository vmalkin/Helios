# THis will generate a simple line plot of solar wind speed for the last 3 carrington rotations
# and highlight repeating events.

import global_config as k
import sqlite3
import time
from datetime import datetime, timezone
# from plotly import graph_objects as go
import numpy as np
from statistics import median, mean
import matplotlib.pyplot as plt

def db_getdata(starttime, satellite_name):
    returnvalues = []
    item = [starttime, satellite_name]
    db = sqlite3.connect(k.solar_wind_database)
    cursor = db.cursor()
    cursor.execute("select * from sw_data where sw_data.sw_time > ? and sw_data.sat_id = ?", item)
    for item in cursor.fetchall():
        returnvalues.append(item)
    return returnvalues


def posix2utc(posixtime, timeformat):
    # '%Y-%m-%d %H:%M'
    utctime = datetime.fromtimestamp(int(posixtime), tz=timezone.utc).strftime(timeformat)
    return utctime


def plot(splitlist, trend, storm, futuredates, sat_id):
    # papercolour = "#d0d0d0"
    plotlist_colours = ['#cfb2be', '#d79180', '#b1493e']
    # plotlist_colours = ['#f1e0e6', '#cfbbc1', '#a49196']
    papercolour = "#f5f5f5"
    gridcolour = "#c0c0c0"
    width = 1500
    height = 550


    plt.figure(figsize=(12, 6))
        # plotdata = go.Scatter(mode="lines")
    # fig = go.Figure(plotdata)
    #
    # Plot the 3 Carrington rotations
    for item in splitlist:
        dates = []
        datas = []
        for value in item:
            dts = value[0]
            dts = posix2utc(dts, '%Y-%m-%d %H:%M')
            dta = value[1]
            dates.append(dts)
            datas.append(dta)
        plt.plot(dates, datas)

    #
    # # plot the averaged forecast
    # fig.add_trace(go.Scatter(x=dates, y=trend, mode="lines", name='Guesstimate', line=dict(color="black", width=4)))
    #
    # # Plot bars showing high solar wind speed over 500km/s
    # marker_colour = 'rgba(50,150,0, 0.1)'
    # fig.add_bar(x=dates, y=storm, name='Storm Period', marker_line_color=marker_colour, marker_line_width=3, marker_color=marker_colour)


    # title = "Solar Wind Guesstimate - Average of last 3 Carrington Rotations."
    # fig.update_layout(width=width, height=height, title=title,
    #                   xaxis_title="Forecast Dates<br><sub>http://DunedinAurora.nz</sub>")
    # fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=gridcolour, nticks=24, tickangle=50)
    # fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=gridcolour)
    # fig.update_layout(font=dict(size=16, color="#202020"), title_font_size=18, )
    # fig.update_layout(plot_bgcolor=papercolour,
    #                   paper_bgcolor=papercolour)
    # fig.add_hline(y=500, line=dict(width=3, color='rgba(10,180,0, 1)'), layer="below",
    #               annotation_font_color='rgba(20,180,0, 1)', annotation_text='Storm Threshold',
    #               annotation_position="top right")
    #
    # # fig.update_yaxes(range=[200, 700])
    # savefile = k.folder_output_to_publish + k.filesep + sat_id + "_simple.jpg"
    # fig.write_image(savefile)
    plt.show()


def create_trend(plotlist):
    avg_readings = []
    # weighting = [0.8, 0.95, 1]
    # weighting = [0.6, 0.8, 1]
    weighting = [1, 1, 1]
    iterations = len(plotlist[0])

    for i in range(0, iterations):
        divisor = 0
        r1 = plotlist[0][i][1]
        if r1 == None:
            r1 = 0
        else:
            r1 = r1 * weighting[0]
            divisor = divisor + 1

        r2 = plotlist[1][i][1]
        if r2 == None:
            r2 = 0
        else:
            r2 = r2 * weighting[1]
            divisor = divisor + 1

        r3 = plotlist[2][i][1]
        if r3 == None:
            r3 = 0
        else:
            r3 = r3 * weighting[2]
            divisor = divisor + 1

        r_sum = (r1 + r2 + r3)

        if r_sum > 0:
            avg = float(r_sum / divisor)
            avg_readings.append(avg)
        else:
            avg_readings.append(None)

    return avg_readings



def posixdate_roundto_minute(value):
    # Round a posix date down to the nearest minute
    i = int(value / 60) * 60
    return i


def split_plotarray(plotarray, starttime, endtime):
    step = (86400 * k.carrington_rotation)
    step = posixdate_roundto_minute(step)
    lower = starttime
    upper = lower + step

    returnlist = []
    tmp = []

    for i in range(0, len(plotarray)):
        plotdate = plotarray[i][0]
        if plotdate >= lower:
            if plotdate < upper:
                tmp.append(plotarray[i])

        if plotdate >= upper:
            # step_multiple = step_multiple + 1
            lower = upper
            upper = upper + step
            returnlist.append(tmp)
            tmp = []
            tmp.append(plotarray[i])

        if plotdate == (endtime - 1):
            returnlist.append(tmp)
    return returnlist


def calc_futuredates(splitdata):
    returnlist = []
    for item in splitdata[2]:
        dt = item[0]
        dt = dt + (k.carrington_rotation * 24 * 60 * 60)
        dt = posix2utc(dt, '%Y-%m-%d %H:%M')
        returnlist.append(dt)
    return returnlist


def create_warnings(trend):
    barvalue = 700
    returnarray = []
    for item in trend:
        if item == None:
            returnarray.append(None)
        if item != None:
            if item > 500:
                returnarray.append(barvalue)
            if item < 500:
                returnarray.append(None)
    return returnarray


def filter_median(trend):
    returnarray = []
    filter_window = 7
    # if len(trend) < filter_half_window * 2:
    #     returnarray = trend
    # else:
    for i in range(0, len(trend)-filter_window):
        t = []
        for j in range(0, filter_window):
            value = trend[i+j]
            if value == None:
                value = 0
            t.append(value)

        m = median(t)
        returnarray.append(m)

    return returnarray


def filter_average(numerical_data, filter_halfwindow):
    # Takes in an array of csv data. single values only.
    returnarray = []

    if len(numerical_data) > 2 * filter_halfwindow + 1:
        for i in range(filter_halfwindow, len(numerical_data) - filter_halfwindow):
            t = []
            for j in range(-filter_halfwindow, filter_halfwindow):
                # if isinstance(numerical_data[i + j], str) is False:
                t.append(float(numerical_data[i + j]))
            v = mean(t)
            returnarray.append(v)
    else:
        print('Unable to average input array')
        returnarray = numerical_data

    return returnarray


def simple_stackplot(sat_id):
    print('*** Begin SW guestimate')
    # start date is three Carington Rotations ago.
    # A day is 86400 seconds long
    day = 86400
    cr = 3 * k.carrington_rotation * day

    # data format:
    # [1693631580, None, 547.1, 0.18, sat_id]
    endtime = time.time()
    endtime = posixdate_roundto_minute(endtime)

    starttime = endtime - cr
    starttime = posixdate_roundto_minute(starttime)

    prunedlist = []
    data = db_getdata(starttime, sat_id)
    # Prune data to only have posixtime and solar wind speed
    for item in data:
        if item[0] > starttime:
            dp = [item[0], item[2]]
            prunedlist.append(dp)

    # Report some basic stats about the data


    # Create a Dictionary of the last three Carrington rotations. This will have the dates, but be empty
    plotarray = {}
    for i in range(starttime, endtime, 60):
        plotarray[i] = None

    # Populate the dictionary of Carrington rotations with data from the database.
    for item in prunedlist:
        date = item[0]
        data = item[1]
        if data < 50:
            data = None
        plotarray[date] = data

    # Convert the dictionary to a plain array
    displaydata = []
    for item in plotarray:
        dp = [item, plotarray[item]]
        displaydata.append(dp)

    # Split the array from [all data], to [[rotation 1], [rotation 2], [rotation 3]] based on the dates.
    splitdata = split_plotarray(displaydata, starttime, endtime)
    futuredates = calc_futuredates(splitdata)

    trend = create_trend(splitdata)
    trend = filter_median(trend)
    trend = filter_average(trend, 60 * 1)
    storm = create_warnings(trend)

    plot(splitdata, trend, storm, futuredates, sat_id)
    print('*** End SW guestimate')

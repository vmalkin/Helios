import sqlite3

import chs_json_data
import chs_sun_img
# import mgr_data
# import mgr_plotter
# import mgr_forecast
import chs_plot
import time
import global_config as k
import sqlite3
import os

# LOGFILE = common_data.reading_actual
# WAITPERIOD = 86400 * 5
__version__ = '4.0'
__author__ = "Vaughn Malkin"

# self._save_image_from_url("https://sdo.gsfc.nasa.gov/assets/img/latest/latest_512_0193.jpg", "sun.jpg")
# self._save_image_from_url("https://services.swpc.noaa.gov/images/suvi-primary-195.png", "sun.jpg")
# self._save_image_from_url("https://services.swpc.noaa.gov/images/animations/suvi/primary/195/latest.png", "sun.jpg")
# solar wind data json http://services.swpc.noaa.gov/products/solar-wind/plasma-2-hour.json


sun = chs_sun_img.SolarImageProcessor("https://services.swpc.noaa.gov/images/animations/suvi/primary/195/latest.png")
#
# data_manager = mgr_data.DataManager(LOGFILE)
# forecaster = mgr_forecast.Forecaster()
# common_data.report_string = ""

def database_create():
    db = sqlite3.connect(k.solar_wind_database)
    cursor = db.cursor()

    # cursor.execute("drop table if exists sw_data;")
    # cursor.execute("drop table if exists imagedata;")
    # cursor.execute("drop table if exists observations;")

    cursor.execute('CREATE TABLE sw_data '
                   '(sw_time integer primary key, '
                   'launch_time integer, '
                   'speed real, '
                   'density real, '
                   'sat_id text);')

    cursor.execute('create table imagedata ('
                   'img_time integer primary key,'
                   'pixel_coverage integer,'
                   'sat_id text'
                   ');')

    cursor.execute('create table observations ('
                   'sw_time integer,'
                   'img_time integer,'
                   'foreign key (sw_time) references sw_data(sw_time),'
                   'foreign key (img_time) references imagedata(img_time)'
                   ');')
    db.commit()
    db.close()


def database_add_sw_data(sat_data, recent_dt):
    db = sqlite3.connect(k.solar_wind_database)
    cursor = db.cursor()
    for item in sat_data:
        if item[0] > recent_dt:
            cursor.execute('insert into sw_data (sw_time, speed, density, sat_id) '
                           'values (?,?,?,?);', item)

    i = [recent_dt]
    r = cursor.execute('select * from sw_data where sw_time > ?', i)
    for item in r:
        print("data added: ", item)

    db.commit()
    db.close()


def database_get_sw_dt(sat_id):
    item = []
    item.append(sat_id)
    db = sqlite3.connect(k.solar_wind_database)
    cursor = db.cursor()
    cursor.execute('select max(sw_time) from sw_data where sw_data.sat_id = ?;', item)
    for item in cursor.fetchone():
        returnvalue = item
    db.close()
    return returnvalue


if __name__ == "__main__":
    # reset the resport string
    k.report_string = ""

    # Check database exists. If not create it.
    if os.path.isfile(k.solar_wind_database) is False:
        print("Creating NEW database")
        database_create()


    # Solar wind data from DSCOVR
    sat_data = chs_json_data.wrapper("http://services.swpc.noaa.gov/products/solar-wind/plasma-2-hour.json")
    datetime_sw = database_get_sw_dt("dscovr")
    # data format:
    # [1693631580, 547.1, 0.18]
    if datetime_sw == None:
        datetime_sw = 0
    for item in sat_data:
        item.append("dscovr")
    database_add_sw_data(sat_data, datetime_sw)

    # Solar wind data from Other Satellites goes here

    # Simple stackplot of solar wind
    chs_plot.simple_stackplot("dscovr")

    # process latest solar image
    # sun.get_meridian_coverage()

    # get current posix time and create the datapoint to append to main data
    # posixtime = int(time.time())   # sun.coverage  discovr.wind_speed  discovr.wind_density
    # dp = mgr_data.DataPoint(posixtime, sun.coverage, discovr.wind_speed, discovr.wind_density)
    # print(dp.return_values())
    #
    # # append the new datapoint and process the master datalist
    # data_manager.append_datapoint(dp)
    # data_manager.process_new_data()
    #
    # # Calculate if enough time has elapsed to start running the forecasting.
    # startdate = int(data_manager.master_data[0].posix_date)
    # nowdate = int(data_manager.master_data[len(data_manager.master_data) - 1].posix_date)
    # elapsedtime = nowdate - startdate
    # timeleft = (WAITPERIOD - elapsedtime) / (60 * 60 * 24)
    #
    # if elapsedtime >= WAITPERIOD:
    #     # create the forecast
    #     forecaster.calculate_forecast(data_manager.master_data)
    #
    #     # Instantiate the prediction plotter, this will load it with the lates values. Plot the final data
    #     prediction_plotter = mgr_plotter.Plotter()
    #     prediction_plotter.plot_data()
    # else:
    #     common_data.report_string = common_data.report_string + ("<br>Insufficient time has passed to begin forecasting. " + str(timeleft)[:5] + " days remaining" + "\n")
    #     print(common_data.report_string)
    #     with open(common_data.regression_ouput, 'w') as w:
    #         w.write(common_data.report_string + '\n')
    #
    #     # Pause for an hour
    # sleeptime = 3600
    # for i in range(sleeptime, 0, -1):
    #     j = i % 60
    #     if j == 0:
    #         mins_left = int(i / 60)
    #         reportstring = "Next download in " + str(mins_left) + " minutes"
    #         print(reportstring)
    #     time.sleep(1)




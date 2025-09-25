# datapoint class to help manage some of the nonsense!
#
# posix_date - the date that corresponds to the current CH reading (posix compliant date)
# coronal_hole_coverage - the coverage at the date (a percentage between 0-1)
# wind_speed - windspeed at the time of posix_date as recorded by DISCOVR (km/s)
# wind_density - wind density at the time of posix_date as recorded by DISCOVR (particles/m^3)

import time
import datetime
from decimal import *
import logging
import os
import common_data

# setup error logging
# logging levels in order of severity:
# DEBUG
# INFO
# WARNING
# ERROR
# CRITICAL
errorloglevel = logging.error
logging.basicConfig(filename="errors.log", format='%(asctime)s %(message)s', level=errorloglevel)
getcontext().prec = 6
CARRINGTON_ROTATION = 655   # hours

# A Datapoint. This is used to store Solar Wind parameters and CH coverage for a particular date.
class DataPoint:
    def __init__(self, posix_date, coronal_hole_coverage, wind_speed, wind_density):
        self.ASTRONOMICAL_UNIT_KM = Decimal(149597900)
        self.posix_date = posix_date
        self.coronal_hole_coverage = Decimal(coronal_hole_coverage)
        self.wind_speed = Decimal(wind_speed)
        self.wind_density = Decimal(wind_density)
        self.process_flag = True

        # A datapoint can also calculate the corrected launchtime of the current wind data, knowing the speed
        # and the size of an astronomical unit
        self.launch_date = float(self.posix_date) - float(self._travel_time())


    # ##############
    # M E T H O D S
    # ##############
    # calculate travel time over 1 AU
    def _travel_time(self):
        if self.wind_speed == 0:
            reportedspeed = 400
        else:
            reportedspeed = self.wind_speed
        travel_time_sec = Decimal(self.ASTRONOMICAL_UNIT_KM) / Decimal(reportedspeed)
        return travel_time_sec

    # allows the object to return a string of it's own parameters
    # handy for quikcly building lists of object propertiezs
    def return_values(self):
        time_now = datetime.datetime.utcfromtimestamp(int(self.posix_date))
        values = str(self.posix_date) + "," + str(self.coronal_hole_coverage) + "," + str(self.wind_speed)  + "," + str(self.wind_density) + "  " + str(time_now)
        return values

    # # convert the internal posx_date to UTC format
    # def _posix2utc(self):
    #     utctime = time.gmtime(int(float(self.posix_date)))
    #     utctime = time.strftime('%Y-%m-%d %H:%M:%S', utctime)
    #     return utctime


# Use to manage a list of datapoints, append, prune list to size, etc.
class DataManager:
    def __init__(self, data_save_file):
        self.data_save_file = data_save_file
        self.master_data = self._load_datapoints(self.data_save_file)


    # ##############
    # M E T H O D S
    # ##############
    def append_datapoint(self, datapoint):
        self.master_data.append(datapoint)

    # def get_utc_time(self):
    #     # returns a STRING of the current UTC time
    #     time_now = str(datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
    #     return time_now

    # def get_posix_time(self):
    #     time_now = time.time()
    #     return time_now

    # Prune the size of the datalist
    def _prune_datalist(self, datalist):
        # Keep the datalist 3 carrington rotations long
        listlength = (CARRINGTON_ROTATION * 3)
        returnlist = []

        if len(datalist) > listlength:
            chop = len(datalist) - listlength
            returnlist = datalist[chop:]
        else:
            returnlist = datalist

        return returnlist

    def _load_datapoints(self, filename):
        # returns an array loaded from the logfile.
        # list in format posix_date, ch_value, windspeed, winddensity
        logging.debug("loading datapoints from CSV: " + filename)

        returnlist = []
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()  # remove \n from EOL
                    datasplit = line.split(",")
                    posixdate = datasplit[0]
                    ch = datasplit[1]
                    speed = datasplit[2]
                    density = datasplit[3]
                    dataitem = DataPoint(posixdate, ch, speed, density)
                    # logging.debug(posixdate + " " + ch + " " + speed + " " + density)
                    returnlist.append(dataitem)
        else:
            print("No logfile. Starting from scratch")
        return returnlist

    # save datapoint list
    def _save_datapoint(self, datapoint_list, filename):
        # list in format posix_date, ch_value, windspeed, winddensity
        logging.debug("SAVING datapoint values to file: " + filename)
        with open(filename, 'w') as f:
            for dpoint in datapoint_list:
                values = str(dpoint.posix_date) + "," + str(dpoint.coronal_hole_coverage) + "," + str(dpoint.wind_speed) + "," + str(dpoint.wind_density)
                f.write(values + '\n')

    # ################################
    # W R A P P E R   F U N C T I O N
    # ################################
    def process_new_data(self):
        self.master_data = self._prune_datalist(self.master_data)
        self._save_datapoint(self.master_data, self.data_save_file)
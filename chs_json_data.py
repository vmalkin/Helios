import requests
import time
import datetime
import global_config as k
from calendar import timegm

def posix2utc(posixtime, timeformat):
    # '%Y-%m-%d %H:%M'
    utctime = datetime.datetime.utcfromtimestamp(int(posixtime)).strftime(timeformat)
    return utctime


def utc2posix(utcstring, timeformat):
    utc_time = time.strptime(utcstring, timeformat)
    epoch_time = timegm(utc_time)
    return epoch_time


def _get_json(data_url):
    # DISCOVR satellite data in JSON format
    # first is the header values, then the data values:
    # ["time_tag","density","speed","temperature"]
    # ["2018-03-19 02:05:00.000","6.35","573.4","330513"]
    try:
        url = data_url
        response = requests.get(url)
        discovr_data = response.json()  # requests has built in json
    except:
        # time_now = str(datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        discovr_data = "no_data"
    return discovr_data


# ################################
# W R A P P E R   F U N C T I O N
# ################################
def wrapper(dataurl):
    returnarray = []
    satdata = _get_json(dataurl)
    if satdata == "no_data":
        # Unable to get DISCOVR data
        k.report_string = k.report_string + "Satellite does not have new solar wind data to report \n"
        dt = 0
        dn = 0
        sp = 0
        returnarray.append([dt, dn, sp])
    else:
        for i in range(1, len(satdata)):
            dt = satdata[i][0]
            dt = int(utc2posix(dt, "%Y-%m-%d %H:%M:%S.%f"))

            dn = satdata[i][1]
            if dn == None:
                dn = -9999
                print("ERROR: Null value in density")
            sp = satdata[i][2]
            if sp == None:
                sp = -9999
                print("ERROR: Null value in speed")

            returnarray.append([dt, sp, dn])
    return returnarray


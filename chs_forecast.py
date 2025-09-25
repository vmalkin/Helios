# This will contain the forecasting algorithm
import math
import time
from decimal import *
import common_data

ASTRONOMICAL_UNIT_KM = 149597900
# prediction_output = "prediction.csv"
prediction_output = common_data.prediction_output
regression_output = common_data.regression_ouput

# median filter on (posicdate, data) list
def median_filter(prediction_list):
    returnlist = []
    for i in range(1, len(prediction_list)-1):
        datalist = []
        ds1 = prediction_list[i-1].split(",")
        ds2 = prediction_list[i].split(",")
        ds3 = prediction_list[i + 1].split(",")
        datetime = ds2[0]
        datalist.append(ds1[1])
        datalist.append(ds2[1])
        datalist.append(ds3[1])
        datalist.sort()
        datavalue = datalist[1]
        dp = datetime + "," + datavalue
        returnlist.append(dp)
    return returnlist


class Forecaster:
    def __init__(self):
        pass

    # convert the internal posx_date to UTC format
    def _posix2utc(self, posix_date):
        utctime = time.gmtime(int(float(posix_date)))
        utctime = time.strftime('%Y-%m-%d %H:%M:%S', utctime)
        return utctime

    # Parse CH coverage the matches the launchdate - return the CH coverage
    # CHData uses a datapoint object to store it's information
    def _CH_match_launchdate(self, CHData, launchdate):
        chcover = 0
        for i in range(1, len(CHData)):
            topvalue = int(CHData[i].posix_date)
            lowervalue = int(CHData[i - 1].posix_date)
            launchdate = int(launchdate)

            if launchdate <= topvalue and  launchdate > lowervalue:
                chcover = CHData[i].coronal_hole_coverage

        return chcover


    # ################################################################
    # Functions required for the Linear Regression
    # taken from "A First Course in applied stats" by Clark and Randal
    # ISBN 978-1-4425-4151-1
    # Pg 70
    # ################################################################
    def _reduce_chdata(self, ch_data):
        #must be run first
        # reduces CH list to just x and y values, strips dates, etc
        returndata = []

        # data is in format a,b,c - we want only b,c
        for item in ch_data:
            datasplit = item.split(",")
            returnitem = datasplit[1] + "," + datasplit[2]
            returndata.append(returnitem)
        return returndata

    def _sum_x(self, xy_list):
        # the sum of x in the xy_list
        # returns a float:
        x_sum = 0

        for item in xy_list:
            datasplit = item.split(",")
            x_value = float(datasplit[0])
            x_sum = float(x_sum + x_value)
        return x_sum

    def _sum_y(self, xy_list):
        # the sum of y in the xy_list
        # returns a float:
        y_sum = 0

        for item in xy_list:
            datasplit = item.split(",")
            y_value = float(datasplit[1])
            y_sum = float(y_sum + y_value)
        return y_sum

    def _sum_x_sqr(self, xy_list):
        # the sum of x^2 in the xy_list
        # returns a float:
        x_sum_sq = 0

        for item in xy_list:
            datasplit = item.split(",")
            x_value = float(datasplit[0])
            x_sum_sq = float(x_sum_sq + math.pow(x_value, 2))
        return x_sum_sq

    def _sum_y_sqr(self, xy_list):
        # the sum of y^2 in the xy_list
        # returns a float
        y_sum_sq = 0

        for item in xy_list:
            datasplit = item.split(",")
            y_value = float(datasplit[1])
            y_sum_sq = float(y_sum_sq + math.pow(y_value, 2))
        return y_sum_sq

    def _sum_x_times_y(self, xy_list):
        # the sum of x*y in the xy_list
        # returns a float
        xy = 0
        for item in xy_list:
            datasplit = item.split(",")
            x = float(datasplit[0])
            y = float(datasplit[1])
            xy = xy + (x * y)
        return xy


    def _mean_x(self, xy_list):
        # the mean of the x values in the xy_list
        # retruns a float
        x_sum = self._sum_x(xy_list)
        x_count = float(len(xy_list))
        x_mean = float(x_sum / x_count)
        return x_mean

    def _mean_y(self, xy_list):
        # the mean of the y values in the xy_list
        # retruns a float
        y_sum = self._sum_y(xy_list)
        y_count = float(len(xy_list))
        y_mean = float(y_sum / y_count)
        return y_mean

    # ################################################################
    # Regression Analysis
    # ################################################################
    def _regression_analysis(self, CH_data):
        # reduce the CH data to x y values only
        xy_data = self._reduce_chdata(CH_data)
        sm_x = self._sum_x(xy_data)
        sm_y = self._sum_y(xy_data)
        sm_x_sqr = self._sum_x_sqr(xy_data)
        sm_y_sqr = self._sum_y_sqr(xy_data)
        sm_x_times_y = self._sum_x_times_y(xy_data)
        mn_x = self._mean_x(xy_data)
        mn_y = self._mean_y(xy_data)
        count_n = len(xy_data)

        sxx = sm_x_sqr - (1 / count_n) * math.pow(sm_x, 2)
        syy = sm_y_sqr - (1 / count_n) * math.pow(sm_y, 2)
        sxy = sm_x_times_y - (1 / count_n) * sm_x * sm_y

        # calculate the a and b values needed for the regression formula
        # y = rg_a + rg_b * x
        rg_b = float(sxy / sxx)
        rg_a = float(mn_y - (rg_b * mn_x))
        pearson_r_value = math.sqrt(math.pow((sxy / math.sqrt(sxx * syy)), 2))
        regression_parameters = [rg_a, rg_b, pearson_r_value]
        return regression_parameters


    # # ################################################################
    # # C A L L   T H I S   W R A P P E R   F U N C T I O N
    # # ################################################################
    def calculate_forecast(self, CH_data):
        # load in the test data
        # parse the data to find the CH date that matches the speed of solar wind
        getcontext().prec = 6

        # the revised data list is will be a python list of data, not objects.
        # revised data will contain a list of [launchdate, windspeed]
        # Windspeed may be zero! Esp if the downlink to the sat fails.
        revised_ch_data = []
        # get the launchdate for each datapoints windspeed
        for data_p in CH_data:
            appenddata = []
            appenddata.append(data_p.launch_date)
            appenddata.append(data_p.wind_speed)
            revised_ch_data.append(appenddata)

        # get the coverage for the launch time
        coverage_data = []
        for item in revised_ch_data:
            coverage = self._CH_match_launchdate(CH_data, item[0])
            date = int(item[0])
            windspeed = item[1]

            # If we have NO wind data, then we should not add this to the final list
            if windspeed > 0:
                if coverage > 0:
                    appenditem = str(date) + "," + str(coverage) + "," + str(windspeed)
                    coverage_data.append(appenditem)
            else:
                pass

        with open("scatterplot.csv", 'w') as w:
            for item in coverage_data:
                w.write(str(item) + '\n')

        # This will create the parameters for a linear model:
        # y = rg_a + rg_b * x
        parameters = self._regression_analysis(coverage_data)
        rg_a = Decimal(parameters[0])
        rg_b = Decimal(parameters[1])
        pearson = Decimal(parameters[2])
        common_data.report_string = common_data.report_string + ("<br>Linear approximation is: Predicted windspeed = " + str(rg_a)[:6] + " + " + str(rg_b)[:6] + " * coronal hole area on meridian     <br>Pearsons correlation |r| = " + str(pearson)[:6] + "\n")
        # regression_values = ("<p>Pearsons correlation: |r| = " + str(pearson)[:6])

        # the array that will hold prediction values
        prediction_list = []
        for item in CH_data:
            predict_speed = rg_a + (rg_b * Decimal(item.coronal_hole_coverage))
            transittime = ASTRONOMICAL_UNIT_KM / predict_speed
            futurearrival = int(item.posix_date) + int(transittime)
            prediction = str(futurearrival) + "," + str(predict_speed)
            prediction_list.append(prediction)

        # remove spikes - Median Filter.
        prediction_list = median_filter(prediction_list)

        with open(prediction_output, 'w') as w:
            for item in prediction_list:
                w.write(str(item) + '\n')

        avg = 0
        for item in CH_data:
            avg = avg + item.wind_speed
        avg_speed = round((avg / len(CH_data)), 1)
        delay_days = round((ASTRONOMICAL_UNIT_KM / avg_speed) / (60 * 60 * 24), 1)
        common_data.report_string = common_data.report_string + ("<br>Average Windspeed is " + str(avg_speed) + "km/s")
        common_data.report_string = common_data.report_string + ("<br>Space weather transit time is " + str(delay_days) + " days")

        print(common_data.report_string)
        with open(regression_output, 'w') as w:
            w.write(common_data.report_string + '\n')
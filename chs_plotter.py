"""
This py manages the plotting of values. It allows me to easily build up a CSV or other file that has
multiple series in it for use in APIS like Highcharts, etc.
"""
import logging
import time
import global_config as k

# setup error logging
# logging levels in order of severity:
# DEBUG
# INFO
# WARNING
# ERROR
# CRITICAL
# errorloglevel = logging.DEBUG
# logging.basicConfig(filename="errors.log", format='%(asctime)s %(message)s', level=errorloglevel)

# READING_PREDICTED = "prediction.csv"
# READING_ACTUAL = "log.csv"
# READING_PREDICTED = common_data.reading_predicted
# READING_ACTUAL = common_data.reading_actual
# NULL = ""

# A plot point, used to aggregate multiple data series for final display.

class PlotPoint:
    def __init__(self, posixdate):
        self.posix_date = posixdate
        self.utcdate = self._posix2utc()
        self.series1value = NULL
        self.series2value = NULL
        self.series3value = NULL
        self.series4value = NULL

    def printvalues(self):
        value = str(self.utcdate) + "," + str(self.series1value) + "," + str(self.series2value) + "," + str(self.series3value) + "," + str(self.series4value)
        return value

    def printlabels(self):
        value = "Date/Time UTC, Speed - Actual, Speed - Forecast, Carrington Rotation Marker, Particle Density Warning"
        return value

    # convert the internal posx_date to UTC format
    def _posix2utc(self):
        utctime = time.gmtime(int(float(self.posix_date)))
        utctime = time.strftime('%Y-%m-%d %H:%M:%S', utctime)
        return utctime

"""
The Plotter class - used to set up the list of plot points, parse thru the multiple lists of series data
and aggregate everything. Creates the final CSV/JSON file to be passed to the website for display via 
Highcharts.
"""
class Plotter:
    def __init__(self):
        self._null = ""
        self._reading_actual = self._load_csv_date_data(READING_ACTUAL)
        self._reading_predicted = self._load_csv_date_data(READING_PREDICTED)
        self._plotlist = []

    # load a CSV file and extract the dates only
    def _load_csv_date_data(self, filename):
        # returns an array loaded from the logfile.
        # list in format posix_date, ch_value, windspeed, winddensity
        logging.debug("loading datapoints from CSV: " + filename)
        returnlist = []
        with open (filename, 'r') as f:
            for line in f:
                line = line.strip()  # remove \n from EOL
                returnlist.append(line)
        return returnlist


    # ################################
    # W R A P P E R   F U N C T I O N
    # ################################
    def plot_data(self):
        # determine the earliest and latest dates for the total data
        # should be Actual Earliest and Predicted Last
        startsplit = self._reading_actual[0].split(",")
        endsplit = self._reading_predicted[len(self._reading_predicted) - 1].split(",")

        startdate = int(startsplit[0])
        enddate = int(endsplit[0])

        # # we are going to set up times at 1hr intervals from the earliest date to most recent.
        # # we will build a list of datapoints with those times to catch the data across both series
        # count = int(((enddate - startdate) / 3600) + 1)
        # # revise the enddate figure so it should be an increment of 3600 from the start date
        # enddate = enddate + (3600 * count)

        # Create the list of datapoints with the appropriate dates in them
        predictionlist = []
        for i in range(startdate, enddate, 3600):
            dp = PlotPoint(i)
            predictionlist.append(dp)

        # SERIES 1 - CH Wind speed ACTUAL
        for item in self._reading_actual:
            itemsplit = item.split(",")
            date = int(itemsplit[0])
            windspeed = itemsplit[2]

            if windspeed == "0":
                windspeed = NULL

            for i in range(1, len(predictionlist)):
                if date <= int(predictionlist[i].posix_date) and date > int(predictionlist[i - 1].posix_date):
                    predictionlist[i].series1value = windspeed

        # SERIES 2 - CH Wind speed PREDICTED
        for item in self._reading_predicted:
            itemsplit = item.split(",")
            date = int(itemsplit[0])
            windspeed = itemsplit[1]

            if windspeed == "0":
                windspeed = NULL

            for i in range(1, len(predictionlist)):
                if date <= int(predictionlist[i].posix_date) and date > int(predictionlist[i - 1].posix_date):
                    predictionlist[i].series2value = windspeed

        # SERIES 3 - Markers for Carrington Rotations. (655 hrs approx)
        for i in range(0, len(predictionlist), 655):
            predictionlist[i].series3value = 500

        # SERIES 4 - Markers for Particle Density over 10p/cm^3
        for item in self._reading_actual:
            DENSITY_THRESHOLD = 10
            itemsplit = item.split(",")
            date = int(itemsplit[0])
            particle_density = float(itemsplit[3])

            if particle_density == "0":
                particle_density = NULL

            for i in range(1, len(predictionlist)):
                if date <= int(predictionlist[i].posix_date) and date > int(predictionlist[i - 1].posix_date):
                    if float(particle_density) > float(DENSITY_THRESHOLD):
                        predictionlist[i].series4value = particle_density
                    else:
                        predictionlist[i].series4value = NULL

        # Save out as a CSV file for display
        try:
            # with open("forecast.csv", "w") as f:
            with open(common_data.csv_mainforecast, "w") as f:
                # create the CSV labels
                null_point = PlotPoint(0)
                f.write(null_point.printlabels() + '\n')

                for plotpt in predictionlist:
                    f.write(plotpt.printvalues() + '\n')
        except:
            print("Unable to write main forecast data to file")

        # Save out as mini CSV file for 7 days display
        try:
            # with open("mini_4cast.csv", "w") as f:
            with open(common_data.csv_miniforecast, "w") as f:
                # create the CSV labels
                null_point = PlotPoint(0)
                f.write(null_point.printlabels() + '\n')

                for i in range(len(predictionlist) - 168, len(predictionlist)):
                    f.write(predictionlist[i].printvalues() + '\n')
        except:
            print("Unable to write mini forecast data to file")

        # Create Plotly Graph for mini prediction.
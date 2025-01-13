import pandas as pd
from datetime import datetime, timedelta
import re
import utm

# Input raw data files logged from phyphox and sensor data
location_file = "ondrone.xls"
air_data_file = "ondrone.txt"

# Read location data excel file into a dataframe
location = pd.ExcelFile(location_file)
location_data = pd.read_excel(location, "Raw Data")
# Create new columns in data frame to store sensor data and local location data
#location_data["x"] = ""
#location_data["y"] = ""
location_data["PCI"] = -1 # Pollution concentration index
location_data["Temperature_(C)"] = -1
location_data["Humidity_(%)"] = -1
location_data["VOC_(PPM)"] = -1
location_data["CO2_(PPM)"] = -1
location_data["PM1.0_(ug/m3)"] = -1
location_data["PM2.5_(ug/m3)"] = -1
location_data["PM10_(ug/m3)"] = -1

# Extract the start time of location data from metadata
time_data = pd.read_excel(location, "Metadata Time")
start_time = datetime.strptime(time_data["system time text"][0].split(" ")[1], "%H:%M:%S.%f")

# Read sensor data file into a list
with open(air_data_file, "r") as file:
    text_lines = file.readlines()

for i, timestamp in enumerate(location_data["Time (s)"]):
    # Convert timestamp in seconds to a datetime, and remove microseconds (for easier comparisons between times)
    location_time = (start_time + timedelta(seconds=timestamp)).replace(microsecond = 0)
    # Update the timestamp in the dataframe
    location_data["Time (s)"][i] = location_time
    # Convert the longitude and latitude to UTM coordinates or x, y (https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system)
    #location_data["x"][i], location_data["y"][i], zone_number, zone_letter = utm.from_latlon(location_data["Latitude (°)"][i], location_data["Longitude (°)"][i])
    # Iterate through the sensor data list
    for data in text_lines:
        # Convert datetime string into datetime object, and remove microseconds (for easier comparisons between times)
        data_time = datetime.strptime(data.split(" ")[0], "%H:%M:%S.%f").replace(microsecond = 0)
        # If the time of the location data and sensor data match (to the nearest second), then GPS location = sensor location
        if location_time.time() == data_time.time():
            # Add sensor data to the dataframe
            parsed_data = data.split()
            try:
                location_data["Temperature_(C)"][i] = float(re.sub("[^0-9.]", "", parsed_data[2]))
                location_data["Humidity_(%)"][i] = float(re.sub("[^0-9.]", "", parsed_data[4]))
                location_data["VOC_(PPM)"][i] = float(re.sub("[^0-9.]", "", parsed_data[6]))
                location_data["CO2_(PPM)"][i] = float(re.sub("[^0-9.]", "", parsed_data[8]))
                location_data["PM1.0_(ug/m3)"][i] = float(re.sub("[^0-9.]", "", parsed_data[10]))
                location_data["PM2.5_(ug/m3)"][i] = float(re.sub("[^0-9.]", "", parsed_data[12]))
                location_data["PM10_(ug/m3)"][i] = float(re.sub("[^0-9.]", "", parsed_data[14]))
                location_data["PCI"][i] = 0.05*location_data["Temperature_(C)"][i] + 0.2*location_data["Humidity_(%)"][i] + 0.5*location_data["VOC_(PPM)"][i] + 0.1*location_data["CO2_(PPM)"][i] + 0.7*location_data["PM1.0_(ug/m3)"][i] + 0.4*location_data["PM2.5_(ug/m3)"][i] + 0.3*location_data["PM10_(ug/m3)"][i]
            except:
                pass
            
# Truncate any GPS point which does not have a matching sensor data point
location_data = location_data[location_data["PCI"] != -1]
# Save the data to a new Excel file
location_data.to_excel(location_file.split(".")[0]+"_modified.xlsx", index = False)

'''
CUSTOM PCI WEIGHTS ARE COMPLETE BS AND RANDOMLY PULLED VALUES FROM MY HEAD. NEED TO MAKE BETTER. BUT AS PROOF OF CONCEPT IT SHOULD WORK? ALSO TALK ABOUT Pollution Concentration Index (PCI) IN REPORT

DO REALISE THAT SOME DATA IS LOST AS WE ARE COMPARING TO THE NEAREST SECOND, EXCLUDING MICROSECONDS. (some data may be lost idk)
SINCE THE RATE OF READING FROM GPS AND SENSOR IS NOT CONSTANT, AND WE ARE TRUNCATING MICROSECONDS, THERE WILL BE DUPLICATED TIMESTAMP VALUES.
THE CODE ONLY LOOKS FOR THE FIRST INSTANCE OF THE VALUE.
SOME DATA MAY BE LOST.
BUT SHOULD NOT BE AN ISSUE AS DISTANCE MOVED BETWEEN MICROSECONDS IS NEGILIBLE
'''
import plotly.express as px
import pandas as pd

location_file = "ondrone_modified.xlsx"
location = pd.ExcelFile(location_file)
location_data = pd.read_excel(location, "Sheet1")


color_scale = [(0, 'green'), (1, 'red')]

fig = px.scatter_mapbox(location_data, 
                        lat="Latitude (°)", 
                        lon="Longitude (°)", 
                        hover_name="PCI", 
                        hover_data=["Temperature_(C)", "Humidity_(%)", "VOC_(PPM)", "CO2_(PPM)", "PM1.0_(ug/m3)", "PM2.5_(ug/m3)", "PM10_(ug/m3)"],
                        color="PCI",
                        color_continuous_scale=color_scale,
                        size="PCI",
                        zoom=8)

fig.update_layout(mapbox_style="open-street-map")
#fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()
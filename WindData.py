import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from datetime import datetime
from datetime import date
import cdsapi
import xarray as xr

df = pd.DataFrame(columns=['lat', 'lon', 'wind_speed'])


st.write('Wind data')

st.sidebar.subheader('Select parameters')
lat_min, lat_max = st.sidebar.slider("Latitude range", 49.0, 61.0, (51.0, 55.0), step=0.1)
lon_min, lon_max = st.sidebar.slider("Longitude range", -8.0, 2.0, (-3.0, 0.0), step=0.1)

date = st.sidebar.date_input('start date', value=datetime(2026, 1, 1))
chart_data = 0
year = str((date).year)
month = f"{(date).month:02d}"
day = f"{(date).day:02d}"

st.write(year, month, day)


polygon_df = pd.DataFrame({
    "polygon": [[
        [lon_max, lat_max],
        [lon_min, lat_max],
        [lon_min, lat_min],
        [lon_max, lat_min],
    ]]
})



polygon_layer = pdk.Layer(
    'PolygonLayer',
    data=polygon_df,
    get_polygon='polygon',
    get_fill_color='[0, 100, 255, 40]',
    get_line_color='[0, 100, 255]',
    line_width_min_pixels=2,
)


fetch_button = st.sidebar.button('Fetch Data')

if fetch_button:
        
        with st.spinner('requesting data from ERA5 - please wait!'):
            
            year = (date).year
            month = f"{(date).month:02d}"
            day = f"{(date).day:02d}"
            
            client = cdsapi.Client()

            dataset = 'reanalysis-era5-single-levels'
            
            request = {
                'product_type': ['reanalysis'],
                'variable': ['100m_u_component_of_wind', '100m_v_component_of_wind'],
                'year': [year],
                'month': [month],
                'day': [day],
                'time': ['00:00', '06:00', '12:00', '18:00'],
                'area': [lat_max, lon_min, lat_min, lon_max],
                'data_format': 'netcdf',
                'download_format': 'unarchived'
            }
            
            
            client.retrieve(dataset, request).download('era5_wind.nc')

            ds = xr.open_dataset('era5_wind.nc')
            
            st.success('Data succesfully retrieved')
            
            wind_speed = np.sqrt(ds['u100']**2 + ds['v100']**2)

            mean_wind = wind_speed.mean(dim='valid_time')
            
            df = mean_wind.to_dataframe(name='wind_speed').reset_index()
            
            df = df.rename(columns={'latitude': 'lat', 'longitude': 'lon'})


            
            
            

st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=55,
        longitude=0,
        zoom=6,
        pitch=50,
    ),
    layers = [polygon_layer, 
              
              
pdk.Layer(
    "ColumnLayer",
    data=df,
    get_position="[lon, lat]",
    get_elevation="wind_speed",
    elevation_scale=2000,        # exaggerates height so differences are visible
    radius=4000,                 # column width in metres - adjust to avoid overlap given 25km spacing
    get_fill_color="[255 - wind_speed * 10, wind_speed * 12, 100, 100]",
    pickable=True,
    auto_highlight=True,
        )
    
    
    
    
] ,
    
    tooltip={
    "html": "<b>Wind Speed:</b> {wind_speed} m/s",
    "style": {
        "backgroundColor": "steelblue",
        "color": "white"
    }
}
))





# -*- coding: utf-8 -*-
"""
Created on Fri Aug  1 21:20:44 2025

@author: mathe
"""

import streamlit as st
import geopandas as gpd
import zipfile, tempfile, os
import pydeck as pdk

def unzip_to_gdf(uploaded_file):
    if not uploaded_file:
        return None
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, uploaded_file.name)
    with open(zip_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)
    shp_files = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.endswith(".shp")]
    if not shp_files:
        return None
    gdf = gpd.read_file(shp_files[0])
    return gdf

st.title("View Two Shapefiles with Pydeck")

polygon_file = st.file_uploader("Upload Polygon Shapefile (ZIP)", type="zip")
point_file = st.file_uploader("Upload Point Shapefile (ZIP)", type="zip")

if polygon_file and point_file and st.button("Process and Show Map"):
    poly_gdf = unzip_to_gdf(polygon_file)
    point_gdf = unzip_to_gdf(point_file)

    if poly_gdf is None or point_gdf is None:
        st.error("One or both shapefiles could not be loaded.")
    else:
        # Prepare polygon data for pydeck (convert geometry to GeoJSON-like)
        poly_gdf["geometry"] = poly_gdf.geometry.simplify(0)  # avoid topology errors

        polygon_layer = pdk.Layer(
            "PolygonLayer",
            data=poly_gdf,
            get_polygon="geometry.coordinates",
            get_fill_color=[0, 128, 255, 80],
            get_line_color=[0, 0, 0],
            pickable=True,
            auto_highlight=True,
        )

        # Prepare point data
        point_gdf["lon"] = point_gdf.geometry.x
        point_gdf["lat"] = point_gdf.geometry.y
        point_layer = pdk.Layer(
            "ScatterplotLayer",
            data=point_gdf,
            get_position='[lon, lat]',
            get_radius=100,
            get_fill_color=[255, 0, 0, 140],
            pickable=True,
            auto_highlight=True,
        )

        # Center view roughly on polygon centroid or average point location
        center_lat = poly_gdf.geometry.centroid.y.mean()
        center_lon = poly_gdf.geometry.centroid.x.mean()

        view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=10)

        r = pdk.Deck(layers=[polygon_layer, point_layer], initial_view_state=view_state,
                     tooltip={"html": "Polygon or Point data", "style": {"color": "white"}})

        st.pydeck_chart(r)

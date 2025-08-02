# -*- coding: utf-8 -*-
"""
Created on Fri Aug  1 18:12:50 2025

@author: mathe
"""

import streamlit as st
import geopandas as gpd
import zipfile, tempfile, os
import leafmap.foliumap as leafmap

st.set_page_config(layout="wide")
st.title("Interactive Shapefile Viewer & Processor")

# File uploaders
polygon_file = st.file_uploader("Upload Polygon Shapefile (ZIP)", type="zip")
point_file = st.file_uploader("Upload Point Shapefile (ZIP)", type="zip")

def unzip_to_gdf(uploaded_file):
    if not uploaded_file:
        return None
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, uploaded_file.name)
    with open(zip_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)
    shp_file = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.endswith(".shp")]
    if not shp_file:
        return None
    return gpd.read_file(shp_file[0])

# Add a Ready button
if st.button("Ready - Process and Show Map"):
    poly_gdf = unzip_to_gdf(polygon_file)
    point_gdf = unzip_to_gdf(point_file)

    if poly_gdf is None and point_gdf is None:
        st.error("Please upload at least one shapefile before clicking Ready.")
    else:
        st.subheader("Processed Map")
        m = leafmap.Map(center=[46.8, -71.2], zoom=10)

        if poly_gdf is not None:
            # Example custom processing: add polygon area
            if poly_gdf.geom_type.iloc[0] in ["Polygon", "MultiPolygon"]:
                poly_gdf["area"] = poly_gdf.area
            m.add_gdf(poly_gdf, layer_name="Polygons")

        if point_gdf is not None:
            # Example custom processing: add lat/lon columns
            point_gdf["lon"] = point_gdf.geometry.x
            point_gdf["lat"] = point_gdf.geometry.y
            m.add_gdf(point_gdf, layer_name="Points", zoom_to_layer=True)

        m.to_streamlit(height=600)

import streamlit as st
from src.na_parkaccess.NA_data_processing import get_place_data
from src.na_parkaccess.NA_analysis import ParkAccessibility
from src.na_parkaccess.NA_visualization import FoliumVisualization

import os
import folium
from streamlit_folium import st_folium

# -------------------------------
# App title
# -------------------------------
st.title("🌳 Park Accessibility Analysis (Any City)")

# -------------------------------
# User inputs
# -------------------------------
place_name = st.text_input("Enter city or country (OpenStreetMap compatible; Example: Kathmandu, Nepal)", "Kathmandu, Nepal")
max_distance = st.number_input("Maximum walking distance (m)", value=1500, min_value=100, max_value=5000, step=100)

# -------------------------------
# Run analysis
# -------------------------------
if st.button("Run Analysis"):
    with st.spinner("Downloading data and computing accessibility..."):
        # Load OSM data
        boundary, parks, buildings, walking_edges = get_place_data(place_name)

        # Initialize model
        access_model = ParkAccessibility(place_name=place_name, target_crs="EPSG:32645")

        # Generate building centroids and park nodes
        buildings_pts, park_nodes = access_model.generate_building_centroids_and_snap(buildings, parks)

        # Compute accessibility
        accessibility_gdf = access_model.compute_accessibility(buildings_pts, park_nodes, max_distance=max_distance)

        st.success("✅ Accessibility analysis complete")
        st.write(accessibility_gdf[[f"park_access_{max_distance}m", "dist_to_park_m"]].head())

        # Generate interactive map
        folium_map = FoliumVisualization.plot_map(
            buildings_gdf=accessibility_gdf,
            street_gdf=walking_edges,
            park_gdf=parks,
            boundary_gdf=boundary,
            city_name=place_name,
            max_distance=max_distance
        )

        # Display map in Streamlit
        st_folium(folium_map, width=800, height=600)

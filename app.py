import streamlit as st
import os
import folium
from streamlit_folium import st_folium

from src.na_parkaccess.NA_data_processing import get_place_data
from src.na_parkaccess.NA_analysis import ParkAccessibility
from src.na_parkaccess.NA_visualization import FoliumVisualization

# -------------------------------
# App title
# -------------------------------
st.title("🌳 Park Accessibility Analysis (Any City)")

# -------------------------------
# User inputs
# -------------------------------
place_name = st.text_input(
    "Enter city or country (OpenStreetMap compatible; Example: Kathmandu, Nepal)",
    "Kathmandu, Nepal"
)
max_distance = st.number_input(
    "Maximum walking distance (m)",
    value=1500,
    min_value=100,
    max_value=5000,
    step=100
)

# -------------------------------
# Helper functions with caching
# -------------------------------
@st.cache_data(show_spinner=True)
def load_place_data(place_name):
    """
    Load boundary, parks, buildings, and walking edges for a given city.
    Cached to prevent repeated downloads.
    """
    return get_place_data(place_name)

@st.cache_resource
def init_access_model(place_name, target_crs="EPSG:32645"):
    """
    Initialize ParkAccessibility model and cache it.
    """
    return ParkAccessibility(place_name=place_name, target_crs=target_crs)

# -------------------------------
# Run analysis
# -------------------------------
if st.button("Run Analysis"):
    with st.spinner("Downloading data and computing accessibility..."):
        # Load data
        boundary, parks, buildings, walking_edges = load_place_data(place_name)

        # Check for empty GeoDataFrames
        if buildings.empty or parks.empty:
            st.warning("❌ No buildings or parks found in this area. Try a different city.")
        else:
            # Initialize model
            access_model = init_access_model(place_name)

            # Generate building centroids and nearest park nodes
            buildings_pts, park_nodes = access_model.generate_building_centroids_and_snap(buildings, parks)

            if not park_nodes:
                st.warning("❌ No park nodes found. Accessibility cannot be computed.")
            else:
                # Compute accessibility
                accessibility_gdf = access_model.compute_accessibility(
                    buildings_pts, park_nodes, max_distance=max_distance
                )

                # Show results
                st.success("✅ Accessibility analysis complete")
                st.dataframe(accessibility_gdf[[f"park_access_{max_distance}m", "dist_to_park_m"]].head())

                # Generate and display map
                folium_map = FoliumVisualization.plot_map(
                    buildings_gdf=accessibility_gdf,
                    street_gdf=walking_edges,
                    park_gdf=parks,
                    boundary_gdf=boundary,
                    city_name=place_name,
                    max_distance=max_distance
                )

                st_folium(folium_map, width=800, height=600)

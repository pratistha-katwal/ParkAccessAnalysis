from src.na_parkaccess.NA_data_processing import get_place_data
from src.na_parkaccess.NA_analysis import ParkAccessibility
from src.na_parkaccess.NA_visualization import FoliumVisualization

import os
import webbrowser

def main():
    # -------------------------------
    # Config
    # -------------------------------
    PLACE_NAME = "Kathmandu, Nepal"   # change to any city/country
    TARGET_CRS = "EPSG:32645"         # UTM zone for Kathmandu
    MAX_DISTANCE = 1500               # meters

    # -------------------------------
    # Load or download datasets
    # -------------------------------
    boundary, parks, buildings, walking_edges = get_place_data(PLACE_NAME)

    # -------------------------------
    # Initialize accessibility model
    # -------------------------------
    access_model = ParkAccessibility(
        place_name=PLACE_NAME,
        target_crs=TARGET_CRS
    )

    # -------------------------------
    # Generate building centroids and park nodes
    # -------------------------------
    buildings_pts, park_nodes = access_model.generate_building_centroids_and_snap(
        buildings,
        parks
    )

    # -------------------------------
    # Compute accessibility
    # -------------------------------
    accessibility_gdf = access_model.compute_accessibility(
        building_centroids_gdf=buildings_pts,
        park_nodes=park_nodes,
        max_distance=MAX_DISTANCE
    )

    # -------------------------------
    # Save output GeoPackage
    # -------------------------------
    os.makedirs("NA_outputs", exist_ok=True)
    out_gpkg = f"NA_outputs/{PLACE_NAME.replace(', ', '_').replace(' ', '_').lower()}_park_access_{MAX_DISTANCE}m.gpkg"

    if not os.path.exists(out_gpkg):
        accessibility_gdf.to_file(out_gpkg, driver="GPKG")

    print("✅ Accessibility analysis complete")
    print(accessibility_gdf[f"park_access_{MAX_DISTANCE}m"].value_counts())

    # -------------------------------
    # Generate interactive Folium map
    # -------------------------------
    m = FoliumVisualization.plot_map(
        buildings_gdf=accessibility_gdf,
        street_gdf=walking_edges,
        park_gdf=parks,
        boundary_gdf=boundary   # matches the parameter name in your FoliumVisualization class
    )

    # Save and open map
    map_path = os.path.abspath("NA_outputs/kathmandu_park_accessibility.html")
    m.save(map_path)
    webbrowser.open(f"file://{map_path}")

if __name__ == "__main__":
    main()

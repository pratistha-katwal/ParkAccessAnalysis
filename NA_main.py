from src.na_parkaccess.NA_data_processing import get_ams_data
from src.na_parkaccess.NA_analysis import ParkAccessibility
from src.na_parkaccess.NA_visualization import FoliumVisualization
from src.na_parkaccess.NA_visualization import MatplotlibVisualization
import os
import webbrowser

def main():
    # -------------------------------
    # Config
    # -------------------------------
    TARGET_CRS = "EPSG:28992"
    MAX_DISTANCE = 1500  # meters

    # -------------------------------
    # Load or download AMS datasets
    # -------------------------------
    ams_boundary, parks_ams, buildings_ams, walking_edges_ams = get_ams_data()

    # -------------------------------
    # Initialize model
    # -------------------------------
    access_model = ParkAccessibility(
        place_name="Amsterdam, Netherlands",
        target_crs=TARGET_CRS
    )

    # -------------------------------
    # Generate centroids and snap to graph
    # -------------------------------
    buildings_pts, park_nodes = access_model.generate_building_centroids_and_snap(
        buildings_ams,
        parks_ams
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
    # Save output
    # -------------------------------
    os.makedirs("NA_outputs", exist_ok=True)
    if not os.path.exists("NA_outputs/buildings_park_access_1500m.gpkg"):
        accessibility_gdf.to_file(
            "NA_outputs/buildings_park_access_1500m.gpkg",
            driver="GPKG"
        )

    print("✅ Accessibility analysis complete")
    print(accessibility_gdf[f"park_access_{MAX_DISTANCE}m"].value_counts())

    m = FoliumVisualization.plot_map(
        buildings_gdf=accessibility_gdf,
        street_gdf=walking_edges_ams,
        park_gdf=parks_ams,
        ams_boundary=ams_boundary
    )

    # Open the map automatically
    map_path = os.path.abspath("NA_outputs/amsterdam_park_accessibility.html")
    webbrowser.open(f"file://{map_path}")

    fig = MatplotlibVisualization.plot_map(building_gdf=accessibility_gdf)
    fig.savefig("NA_outputs/amsterdam_park_accessibility_matplotlib.png")
    print("✅ Map generated and saved to NA_outputs/amsterdam_park_accessibility.html")
if __name__ == "__main__":
    main()

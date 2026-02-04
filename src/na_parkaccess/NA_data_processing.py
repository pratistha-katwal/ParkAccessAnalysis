import geopandas as gpd
import osmnx as ox
import os
from shapely.geometry import Polygon, MultiPolygon

# ==================================================
# OSM Boundary (Generic: City / Region / Country)
# ==================================================
class OSMBoundary:
    """Download administrative boundary from OpenStreetMap"""

    def __init__(self, place_name):
        self.place_name = place_name
        self.boundary_gdf = None

    def download_boundary(self):
        self.boundary_gdf = ox.geocode_to_gdf(self.place_name).to_crs(epsg=4326)
        return self.boundary_gdf


# ==================================================
# Parks
# ==================================================
class Parks:
    """Download and process park polygons from OpenStreetMap"""

    @staticmethod
    def get_parks(place_name):
        tags = {"leisure": "park"}
        parks = ox.features_from_place(place_name, tags=tags)
        parks = parks[parks.geometry.type.isin(["Polygon", "MultiPolygon"])]
        return parks.to_crs(epsg=4326)


# ==================================================
# Buildings
# ==================================================
class Buildings:
    """Download and process building polygons from OpenStreetMap"""

    @staticmethod
    def get_buildings(place_name):
        tags = {"building": True}
        buildings = ox.features_from_place(place_name, tags=tags)
        buildings = buildings[buildings.geometry.type.isin(["Polygon", "MultiPolygon"])]
        return buildings.to_crs(epsg=4326)


# ==================================================
# Walking Network
# ==================================================
class WalkingNetwork:
    """Download and process walking network from OpenStreetMap"""

    @staticmethod
    def get_edges(place_name):
        G = ox.graph_from_place(place_name, network_type="walk")
        nodes, edges = ox.graph_to_gdfs(G)
        return nodes.to_crs(epsg=4326), edges.to_crs(epsg=4326)


# ==================================================
# Clipping utilities
# ==================================================
class ClipData:
    """Spatial clipping utilities"""

    @staticmethod
    def clip_to_boundary(gdf, boundary):
        return gpd.clip(gdf, boundary)


# ==================================================
# Helpers
# ==================================================
def clean_gpkg_columns(gdf):
    """
    Clean column names to be GeoPackage-compatible and remove duplicates
    """
    gdf = gdf.copy()

    # Sanitize column names
    cols = (
        gdf.columns
        .astype(str)
        .str.replace(" ", "_", regex=False)
        .str.replace(":", "_", regex=False)
        .str.replace("-", "_", regex=False)
        .str.replace("/", "_", regex=False)
        .str.lower()
    )

    # Deduplicate column names
    seen = {}
    new_cols = []
    for c in cols:
        if c in seen:
            i = 1
            new_name = f"{c}_{i}"
            while new_name in seen:
                i += 1
                new_name = f"{c}_{i}"
            new_cols.append(new_name)
            seen[new_name] = True
        else:
            new_cols.append(c)
            seen[c] = True

    gdf.columns = new_cols
    return gdf


# ==================================================
# Main pipeline
# ==================================================
def get_place_data(place_name, out_dir="NA_outputs"):
    os.makedirs(out_dir, exist_ok=True)

    safe_name = place_name.replace(", ", "_").replace(" ", "_").lower()

    boundary_file = f"{out_dir}/{safe_name}_boundary.gpkg"
    parks_file = f"{out_dir}/{safe_name}_parks.gpkg"
    buildings_file = f"{out_dir}/{safe_name}_buildings.gpkg"
    walking_edges_file = f"{out_dir}/{safe_name}_walking_edges.gpkg"

    # Load from disk if exists
    if all(os.path.exists(f) for f in [boundary_file, parks_file, buildings_file, walking_edges_file]):
        boundary = gpd.read_file(boundary_file)
        parks_clip = gpd.read_file(parks_file)
        buildings_clip = gpd.read_file(buildings_file)
        walking_edges_clip = gpd.read_file(walking_edges_file)
        print("Loaded data from disk.")
    else:
        print("Downloading data from OpenStreetMap...")

        # Boundary
        boundary_obj = OSMBoundary(place_name)
        boundary = boundary_obj.download_boundary()
        boundary.to_file(boundary_file, driver="GPKG")

        # OSM features
        parks = Parks.get_parks(place_name)
        buildings = Buildings.get_buildings(place_name)
        walking_nodes, walking_edges = WalkingNetwork.get_edges(place_name)

        # Clip
        parks_clip = ClipData.clip_to_boundary(parks, boundary)
        buildings_clip = ClipData.clip_to_boundary(buildings, boundary)
        walking_edges_clip = ClipData.clip_to_boundary(walking_edges, boundary)

        # Clean columns
        parks_clip = clean_gpkg_columns(parks_clip)
        buildings_clip = clean_gpkg_columns(buildings_clip)
        walking_edges_clip = clean_gpkg_columns(walking_edges_clip)

        # Save
        parks_clip.to_file(parks_file, driver="GPKG")
        buildings_clip.to_file(buildings_file, driver="GPKG")
        walking_edges_clip.to_file(walking_edges_file, driver="GPKG")

        print("Downloaded and saved all data.")

    return boundary, parks_clip, buildings_clip, walking_edges_clip


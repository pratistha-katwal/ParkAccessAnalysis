
import requests
import geopandas as gpd
from shapely.geometry import shape
import osmnx as ox
import os


# ==================================================
# Amsterdam Municipality Boundary
# ==================================================
class AmsterdamBoundary:
    """
    Download and process Amsterdam municipality boundary from PDOK WFS
    """

    def __init__(self):
        self.url = "https://service.pdok.nl/kadaster/bestuurlijkegebieden/wfs/v1_0"
        self.params = {
            "service": "WFS",
            "request": "GetFeature",
            "version": "2.0.0",
            "typeNames": "bg:Gemeentegebied",
            "outputFormat": "application/json",
        }
        self.gemeente_gdf = None
        self.ams_boundary = None

    def download_data(self):
        response = requests.get(self.url, params=self.params)
        if response.status_code == 200:
            return response.json()
        else:
            raise RuntimeError(
                f"Failed to download WFS data (status {response.status_code})"
            )

    def to_geodataframe(self, data_json):
        features = data_json["features"]
        geometries = [shape(f["geometry"]) for f in features]
        properties = [f["properties"] for f in features]

        self.gemeente_gdf = gpd.GeoDataFrame(
            properties, geometry=geometries, crs="EPSG:28992"
        ).to_crs(epsg=4326)

        return self.gemeente_gdf

    def filter_amsterdam(self):
        if self.gemeente_gdf is None:
            raise RuntimeError("Run to_geodataframe() first")

        ams = self.gemeente_gdf[self.gemeente_gdf["naam"] == "Amsterdam"]

        # Dissolve in case of multiple polygons
        self.ams_boundary = ams.dissolve()

        return self.ams_boundary


# ==================================================
# Parks
# ==================================================
class Parks:
    """Download and process park polygons from OpenStreetMap"""

    @staticmethod
    def get_parks():
        tags = {"leisure": "park"}
        parks = ox.features_from_place("Amsterdam, Netherlands", tags=tags)

        parks = parks[parks.geometry.type.isin(["Polygon", "MultiPolygon"])]
        parks = parks.to_crs(epsg=4326)

        return parks


# ==================================================
# Buildings
# ==================================================
class Buildings:
    """Download and process building polygons from OpenStreetMap"""

    @staticmethod
    def get_buildings():
        tags = {"building": True}
        buildings = ox.features_from_place("Amsterdam, Netherlands", tags=tags)

        buildings = buildings[buildings.geometry.type.isin(["Polygon", "MultiPolygon"])]
        buildings = buildings.to_crs(epsg=4326)

        return buildings


# ==================================================
# Walking Network
# ==================================================
class WalkingNetwork:
    """Download and process Amsterdam walking network"""

    @staticmethod
    def get_edges():
        G = ox.graph_from_place("Amsterdam, Netherlands", network_type="walk")
        

        nodes, edges = ox.graph_to_gdfs(G)
        nodes = nodes.to_crs(epsg=4326)
        edges = edges.to_crs(epsg=4326)

        return G, nodes, edges


# ==================================================
# Clipping utilities
# ==================================================
class ClipData:
    """Spatial clipping utilities"""

    @staticmethod
    def clip_to_amsterdam(gdf, ams_boundary):
        return gpd.clip(gdf, ams_boundary)




def get_ams_data():
    os.makedirs("NA_outputs", exist_ok=True)

    files = [
        "NA_outputs/ams_boundary.gpkg",
        "NA_outputs/parks_ams.gpkg",
        "NA_outputs/buildings_ams.gpkg",
        "NA_outputs/walking_edges_ams.gpkg",
    ]

    # check if all files exist
    if all(os.path.exists(f) for f in files):
        ams_boundary = gpd.read_file(files[0])
        parks_ams = gpd.read_file(files[1])
        buildings_ams = gpd.read_file(files[2])
        walking_edges_ams = gpd.read_file(files[3])
    else:
        # Download boundary
        boundary = AmsterdamBoundary()
        boundary_json = boundary.download_data()
        ams_boundary = boundary.to_geodataframe(boundary_json)
        ams_boundary = boundary.filter_amsterdam()
        ams_boundary.to_file("NA_outputs/ams_boundary.gpkg")

        # Download OSM data
        parks = Parks.get_parks()
        buildings = Buildings.get_buildings()
        walking_graph, walking_nodes, walking_edges = WalkingNetwork.get_edges()

        # Clip
        parks_ams = ClipData.clip_to_amsterdam(parks, ams_boundary)
        buildings_ams = ClipData.clip_to_amsterdam(buildings, ams_boundary)
        # walking_graph_ams = ClipData.clip_to_amsterdam(walking_graph, ams_boundary)
        walking_nodes_ams = ClipData.clip_to_amsterdam(walking_nodes, ams_boundary)
        walking_edges_ams = ClipData.clip_to_amsterdam(walking_edges, ams_boundary)

        # Save
        parks_ams.to_file("NA_outputs/parks_ams.gpkg", driver="GPKG")
        buildings_ams.to_file("NA_outputs/buildings_ams.gpkg", driver="GPKG")
        walking_nodes_ams.to_file("NA_outputs/walking_nodes_ams.gpkg", driver="GPKG")
        walking_edges_ams.to_file("NA_outputs/walking_edges_ams.gpkg", driver="GPKG")

    return ams_boundary, parks_ams, buildings_ams, walking_edges_ams

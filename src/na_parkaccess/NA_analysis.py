import osmnx as ox
import networkx as nx
import geopandas as gpd

class ParkAccessibility:
    def __init__(self, place_name, target_crs="EPSG:32645"):
        """
        Initialize walking network for accessibility analysis.
        Graph download is heavy, so this should be cached in Streamlit.
        """
        self.target_crs = target_crs

        # Download graph
        self.G = ox.graph_from_place(place_name, network_type="walk")
        # Project graph to target CRS
        self.G = ox.project_graph(self.G, to_crs=target_crs)

    # -------------------------------
    # Prepare buildings & parks
    # -------------------------------
    def generate_building_centroids_and_snap(self, buildings_gdf, parks_gdf):
        """
        Compute centroids and snap to nearest nodes.
        Returns:
            buildings_gdf with nearest_node column, list of park node IDs
        """
        # Defensive copies
        buildings = buildings_gdf.copy()
        parks = parks_gdf.copy()

        # Ensure CRS is projected
        buildings = buildings.to_crs(self.target_crs)
        parks = parks.to_crs(self.target_crs)

        # Compute centroids
        buildings["geometry"] = buildings.geometry.centroid
        parks["geometry"] = parks.geometry.centroid

        # Snap buildings to nearest nodes
        if not buildings.empty:
            buildings["nearest_node"] = ox.nearest_nodes(
                self.G,
                X=buildings.geometry.x,
                Y=buildings.geometry.y
            )
        else:
            buildings["nearest_node"] = []

        # Snap parks to nearest nodes
        if not parks.empty:
            park_nodes = ox.nearest_nodes(
                self.G,
                X=parks.geometry.x,
                Y=parks.geometry.y
            )
            park_nodes = list(set(park_nodes))
        else:
            park_nodes = []

        return buildings, park_nodes

    # -------------------------------
    # Network accessibility
    # -------------------------------
    def compute_accessibility(self, building_centroids_gdf, park_nodes, max_distance=1500):
        """
        Compute network-based accessibility of buildings to parks.
        Adds columns:
            - dist_to_park_m
            - park_access_{max_distance}m
        """
        gdf = building_centroids_gdf.copy()

        # Dijkstra distances
        if park_nodes:
            distances = nx.multi_source_dijkstra_path_length(
                self.G,
                park_nodes,
                cutoff=max_distance,
                weight="length"
            )
        else:
            distances = {}

        # Map distances to buildings
        gdf["dist_to_park_m"] = gdf["nearest_node"].map(distances)
        gdf[f"park_access_{max_distance}m"] = gdf["dist_to_park_m"].notnull()

        return gdf

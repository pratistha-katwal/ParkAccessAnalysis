import osmnx as ox
import networkx as nx


class ParkAccessibility:
    def __init__(self, place_name, target_crs="EPSG:28992"):
        """
        Initialize walking network for accessibility analysis
        """
        self.target_crs = target_crs

        self.G = ox.graph_from_place(
            place_name,
            network_type="walk"
        )
        self.G = ox.project_graph(self.G, to_crs=target_crs)

    # -----------------------------------
    # Prepare buildings & parks
    # -----------------------------------
    def generate_building_centroids_and_snap(
        self,
        buildings_gdf,
        parks_gdf
    ):
        # Buildings → centroids → nearest nodes
        buildings = buildings_gdf.copy()
        buildings = buildings.to_crs(self.target_crs)
        buildings["geometry"] = buildings.geometry.centroid
        buildings["nearest_node"] = ox.nearest_nodes(
            self.G,
            buildings.geometry.x,
            buildings.geometry.y
        )

        # Parks → centroids → nearest nodes
        parks = parks_gdf.copy()
        parks = parks.to_crs(self.target_crs)
        parks["geometry"] = parks.geometry.centroid
        park_nodes = ox.nearest_nodes(
            self.G,
            parks.geometry.x,
            parks.geometry.y
        )

        return buildings, list(set(park_nodes))

    # -----------------------------------
    # Network accessibility
    # -----------------------------------
    def compute_accessibility(
        self,
        building_centroids_gdf,
        park_nodes,
        max_distance=1500
    ):
        gdf = building_centroids_gdf.copy()

        distances = nx.multi_source_dijkstra_path_length(
            self.G,
            park_nodes,
            cutoff=max_distance,
            weight="length"
        )

        gdf["dist_to_park_m"] = gdf["nearest_node"].map(distances)
        gdf[f"park_access_{max_distance}m"] = gdf["dist_to_park_m"].notnull()
        print("Data overview:")
        print(f"Total buildings: {len(gdf)}")
        print(f"Buildings with park_access_1500m=True: {gdf['park_access_1500m'].sum()}")
        print(f"Buildings with park_access_1500m=False: {(~gdf['park_access_1500m']).sum()}")

        # Check for NaN/inf values in distance column
        print(f"\nDistance column statistics:")
        print(f"Min distance: {gdf['dist_to_park_m'].min()}")
        print(f"Max distance: {gdf['dist_to_park_m'].max()}")
        print(f"Mean distance: {gdf['dist_to_park_m'].mean()}")

        return gdf

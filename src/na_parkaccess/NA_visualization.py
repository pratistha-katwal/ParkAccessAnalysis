import folium
import geopandas as gpd
import os
import webbrowser
from folium.plugins import MarkerCluster

class FoliumVisualization:
    @staticmethod
    def plot_map(buildings_gdf, street_gdf, park_gdf, boundary_gdf, city_name="City", max_distance=1500):
        """
        Plot park accessibility for residential buildings in a city using Folium.
        Uses MarkerCluster to speed up rendering for large datasets.
        """
        # -----------------------------
        # Ensure CRS is EPSG:4326
        # -----------------------------
        buildings_gdf = buildings_gdf.to_crs(epsg=4326)
        street_gdf = street_gdf.to_crs(epsg=4326)
        park_gdf = park_gdf.to_crs(epsg=4326)
        boundary_gdf = boundary_gdf.to_crs(epsg=4326)

        if "dist_to_park_m" not in buildings_gdf.columns:
            buildings_gdf["dist_to_park_m"] = max_distance + 500

        # -----------------------------
        # Compute centroid for map center
        # -----------------------------
        centroid = boundary_gdf.geometry.centroid.iloc[0]
        m = folium.Map(location=[centroid.y, centroid.x], zoom_start=14)

        # -----------------------------
        # Add boundary, streets, parks
        # -----------------------------
        folium.GeoJson(
            boundary_gdf,
            name=f"{city_name} Boundary",
            style_function=lambda x: {"fillColor": "none", "color": "blue", "weight": 2}
        ).add_to(m)

        folium.GeoJson(
            street_gdf,
            name="Walking Network",
            style_function=lambda x: {"color": "gray", "weight": 1}
        ).add_to(m)

        folium.GeoJson(
            park_gdf,
            name="Parks",
            style_function=lambda x: {"fillColor": "green", "color": "green", "weight": 1, "fillOpacity": 0.6}
        ).add_to(m)

        # -----------------------------
        # Add buildings using MarkerCluster
        # -----------------------------
        marker_cluster = MarkerCluster(name="Buildings").add_to(m)

        for _, row in buildings_gdf.iterrows():
            dist = row.get("dist_to_park_m", max_distance + 500)
            accessible = row.get(f"park_access_{max_distance}m", False)

            if not accessible:
                color = "red"
            elif dist <= 500:
                color = "green"
            elif dist <= 1000:
                color = "yellow"
            elif dist <= max_distance:
                color = "orange"
            else:
                color = "red"

            folium.CircleMarker(
                location=[row.geometry.y, row.geometry.x],
                radius=2,
                color=color,
                fill=True,
                fill_opacity=0.5,
                popup=f"Distance: {dist:.0f} m<br>Accessible: {'Yes' if accessible else 'No'}"
            ).add_to(marker_cluster)

        # -----------------------------
        # Add legend & title
        # -----------------------------
        legend_html = f"""
        <div style="position: fixed; bottom: 50px; left: 50px;
                    background-color: white; padding: 10px;
                    border: 2px solid grey; z-index: 9999; font-size: 12px;">
            <b>Park Accessibility</b><br><br>
            <span style="color:green">●</span> 0–500 m<br>
            <span style="color:yellow">●</span> 500–1000 m<br>
            <span style="color:orange">●</span> 1000–{max_distance} m<br>
            <span style="color:red">●</span> Not accessible<br><br>
            Parks <span style="background:green; display:inline-block; width:15px; height:10px; margin-left:5px;"></span><br>
            Street Network <span style="background:gray; display:inline-block; width:15px; height:10px; margin-left:5px;"></span><br>
            City Boundary <span style="border:3px solid blue; display:inline-block; width:15px; height:10px; margin-left:5px;"></span><br>
        </div>
        """
        title_html = f"""
        <h3 align="center" style="font-size:20px">
            Accessibility of Residential Buildings to Public Parks in {city_name} (≤ {max_distance} m Walking Distance)
        </h3>
        """

        m.get_root().html.add_child(folium.Element(title_html))
        m.get_root().html.add_child(folium.Element(legend_html))

        # -----------------------------
        # Save map
        # -----------------------------
        os.makedirs("NA_outputs", exist_ok=True)
        map_file = f"NA_outputs/{city_name.replace(' ', '_').lower()}_park_accessibility.html"
        m.save(map_file)

        # -----------------------------
        # Open automatically in web browser
        # -----------------------------
        # webbrowser.open(f"file://{os.path.abspath(map_file)}")

        print(f"✅ Map saved and opened at {map_file}")
        return m

class FoliumVisualization:
    @staticmethod
    def plot_map(buildings_gdf, street_gdf, park_gdf, ams_boundary):
        import folium
        import geopandas as gpd
        import os

        # -----------------------------
        # Ensure CRS is EPSG:4326
        # -----------------------------
        buildings_gdf = buildings_gdf.to_crs(epsg=4326)
        street_gdf = street_gdf.to_crs(epsg=4326)
        park_gdf = park_gdf.to_crs(epsg=4326)
        ams_boundary = ams_boundary.to_crs(epsg=4326)

        buildings_gdf["dist_to_park_m"] = buildings_gdf["dist_to_park_m"].fillna(2000)

        # -----------------------------
        # Map center
        # -----------------------------
# Compute centroid safely in projected CRS
        ams_proj = ams_boundary.to_crs(epsg=28992)
        centroid_proj = ams_proj.geometry.centroid.iloc[0]
        centroid = gpd.GeoSeries([centroid_proj], crs=28992).to_crs(epsg=4326).iloc[0]

        m = folium.Map(location=[centroid.y, centroid.x], zoom_start=14)

        # -----------------------------
        # Boundary
        # -----------------------------
        folium.GeoJson(
            ams_boundary,
            name="Amsterdam Boundary",
            style_function=lambda x: {
                "fillColor": "none",
                "color": "blue",
                "weight": 2
            }
        ).add_to(m)

        # -----------------------------
        # Street network
        # -----------------------------
        folium.GeoJson(
            street_gdf,
            name="Walking Network",
            style_function=lambda x: {
                "color": "gray",
                "weight": 1
            }
        ).add_to(m)

        # -----------------------------
        # Parks
        # -----------------------------
        folium.GeoJson(
            park_gdf,
            name="Parks",
            style_function=lambda x: {
                "fillColor": "green",
                "color": "green",
                "weight": 1,
                "fillOpacity": 0.6
            }
        ).add_to(m)

        # -----------------------------
        # Buildings
        # -----------------------------
        for _, row in buildings_gdf.iterrows():
            dist = row["dist_to_park_m"]
            accessible = row["park_access_1500m"]

            if not accessible:
                color = "red"
            elif dist <= 500:
                color = "green"
            elif dist <= 1000:
                color = "yellow"
            elif dist <= 1500:
                color = "orange"
            else:
                color = "red"

            folium.CircleMarker(
                location=[row.geometry.y, row.geometry.x],
                radius=1,
                color=color,
                fill=True,
                fill_opacity=0.4,
                popup=f"Distance: {dist:.0f} m<br>Accessible: {'Yes' if accessible else 'No'}"
            ).add_to(m)

        # -----------------------------
        # Layer control
        # -----------------------------
        folium.LayerControl().add_to(m)

        # -----------------------------
        # Legend
        # -----------------------------
        legend_html = """
        <div style="position: fixed; bottom: 50px; left: 50px;
                    background-color: white; padding: 10px;
                    border: 2px solid grey; z-index: 9999;
                    font-size: 12px;">
            <b>Park Accessibility</b><br><br>

            <span style="color:green">●</span> 0–500 m<br>
            <span style="color:yellow">●</span> 500–1000 m<br>
            <span style="color:orange">●</span> 1000–1500 m<br>
            <span style="color:red">●</span> Not accessible<br><br>

            
            Parks <span style="background:green; display:inline-block; width:15px; height:10px; margin-left:5px;"></span><br>
            Street Network <span style="background:gray; display:inline-block; width:15px; height:10px; margin-left:5px;"></span><br>
            City Boundary <span style="border:3px solid blue; display:inline-block; width:15px; height:10px; margin-left:5px;"></span><br>
            
        </div>
        """
        title_html = """
        <h3 align="center" style="font-size:20px">
            Accessibility of Residential Buildings to Public Parks in Amsterdam (≤ 1500 m Walking Distance)
        </h3>
        """

        m.get_root().html.add_child(folium.Element(title_html))


        m.get_root().html.add_child(folium.Element(legend_html))
        m.save("NA_outputs/amsterdam_park_accessibility.html")
        m
        return m

class MatplotlibVisualization:
    @staticmethod
    def plot_map(building_gdf):
        import matplotlib.pyplot as plt

        counts = building_gdf["park_access_1500m"].value_counts()

        labels = ["Covered (≤1500 m)", "Not Covered (>1500 m)"]
        values = [counts.get(True, 0), counts.get(False, 0)]

        fig, ax = plt.subplots(figsize=(6, 5))
        bars = ax.bar(labels, values)

        # Add value labels
        for bar in bars:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{int(bar.get_height()):,}",
                ha="center",
                va="bottom"
            )

        ax.set_ylabel("Number of Households")
        ax.set_title("Household Access to Parks (1500 m Walking Distance)")
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        fig.savefig("NA_outputs/amsterdam_park_accessibility_bar.png", dpi=300)

        plt.tight_layout()
        plt.show()
        return fig


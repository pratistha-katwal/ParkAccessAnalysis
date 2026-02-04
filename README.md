

# Park Accessibility Analysis 🌳🏙️

This project analyzes **walking accessibility of residential buildings to public parks** in any city using **OpenStreetMap (OSM) data** and **network-based distance analysis**. Accessibility is evaluated using a **1500 m walking distance threshold**, commonly applied in urban planning and public health studies.

The workflow integrates **geospatial data processing**, **graph-based network analysis**, and **interactive visualizations**.

---

## 📌 Project Objectives

* Assess residential access to public parks in any city
* Use **network-based walking distance** instead of straight-line distance
* Identify buildings with and without park access within 1500 m
* Produce reproducible spatial and visual outputs, including an **interactive map**

---

## 🗂 Project Structure

```
├── NA_main.py
├── pyproject.toml
├── poetry.lock
├── README.md
├── src
│   └── na_parkaccess
│       ├── __init__.py
│       ├── NA_analysis.py
│       ├── NA_data_processing.py
│       └── NA_visualization.py
└── tests
    └── __init__.py
```

---

## 🧠 Methodology Overview

### Data Sources

* **Administrative boundary**: OpenStreetMap (`geocode_to_gdf`)
* **Parks**: OpenStreetMap (`leisure=park`)
* **Buildings**: OpenStreetMap (`building=*`)
* **Walking network**: OpenStreetMap pedestrian network

### Analysis Steps

1. Download and clip datasets to the city boundary
2. Convert buildings and parks to centroid points
3. Snap points to the walking network
4. Calculate shortest walking distance using Dijkstra's algorithm
5. Classify buildings based on a 1500 m accessibility threshold

---

## 🛠 Installation & Setup

### Prerequisites

* Python ≥ 3.11
* Git
* Poetry

### Clone Repository

```bash
git clone https://github.com/pratistha-katwal/Amsterdam_ParkAccessibility.git
cd Amsterdam_ParkAccessibility
```

### Install Dependencies

```bash
poetry install
```

### Activate the Environment

```bash
poetry shell
```

### Run the Main File

```bash
python NA_main.py
```

> Change `PLACE_NAME` in `NA_main.py` to the city or region you want to analyze, e.g., `"Kathmandu, Nepal"`.

---

## 📊 Output

After running the project, a folder named `NA_outputs` will be created containing:

* **GeoPackage files** (`.gpkg`) for city boundaries, parks, buildings, and walking network
* **Maps and visualizations** (`.html` and `.png`) showing park accessibility

### Viewing the Interactive Map

The map is automatically opened in your default web browser after running the main script.
You can also open it manually:

```bash
open NA_outputs/<city_name>_park_accessibility.html
```

---

## 📈 Sample Results (Example: Kathmandu)

### Data Overview

* **Total buildings**: 149277
* **Buildings with park access** within 1500 m: 145184
* **Buildings without park access** within 1500 m: 4093

### Distance Statistics

* **Minimum distance** to nearest park: 0.0 m
* **Maximum distance** to nearest park: 1,499.7 m
* **Mean distance** to nearest park: 591.1 m

---

## 🔗 References

* OpenStreetMap: [https://www.openstreetmap.org](https://www.openstreetmap.org)
* NetworkX library: [https://networkx.org](https://networkx.org)



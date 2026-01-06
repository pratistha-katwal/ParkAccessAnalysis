# Amsterdam Park Accessibility Analysis 🇳🇱🌳

This project analyzes **walking accessibility of residential buildings to public parks in Amsterdam** using **OpenStreetMap data** and **network-based distance analysis**.  
Accessibility is evaluated using a **1500 m walking distance threshold**, commonly applied in urban planning and public health studies.

The workflow integrates **geospatial data processing**, **graph-based network analysis**, and **interactive visualizations**.

---

## 📌 Project Objectives

- Assess residential access to public parks in Amsterdam
- Use **network-based walking distance** instead of straight-line distance
- Identify buildings with and without park access within 1500 m
- Produce reproducible spatial and visual outputs

---

## 🗂 Project Structure


├── NA_main.py
├── pyproject.toml
├── poetry.lock
├── README.md
├── src
│ └── na_parkaccess
│ ├── init.py
│ ├── NA_analysis.py
│ ├── NA_data_processing.py
│ └── NA_visualization.py
└── tests
└── init.py


---

## 🧠 Methodology Overview

### Data Sources
- **Administrative boundary**: PDOK (Kadaster)
- **Parks**: OpenStreetMap (`leisure=park`)
- **Buildings**: OpenStreetMap (`building=*`)
- **Walking network**: OpenStreetMap pedestrian network

### Analysis Steps
1. Download and clip datasets to Amsterdam boundary
2. Convert buildings and parks to centroid points
3. Snap points to the walking network
4. Calculate shortest walking distance using Dijkstra’s algorithm
5. Classify buildings based on a 1500 m accessibility threshold

---

## 🛠 Installation & Setup

### Prerequisites
- Python ≥ 3.11
- Git
- Poetry

### Clone Repository
```bash
git clone https://github.com/pratistha-katwal/Amsterdam_ParkAccessibility.git
cd Amsterdam_ParkAccessibility
Install Dependencies
bash
Copy code
poetry install
Activate the Environment
bash
Copy code
poetry shell
Run the Main File
bash
Copy code
python NA_main.py

### Output
After running the project, a folder named NA_outputs will be created. This folder contains:

Shapefiles and GeoPackage files (.gpkg) for Amsterdam boundaries, parks, buildings, and walking network

Maps and visualizations (.html and .png) showing park accessibility

Viewing the Map
Open the HTML file in a browser to interactively explore park accessibility:

bash
Copy code
NA_outputs/amsterdam_park_accessibility.html
Sample Data Overview

Total buildings: 197,057

Buildings with park access within 1500 m: 190,120

Buildings without park access within 1500 m: 6,937

Distance Statistics

Minimum distance to nearest park: 0.0 m

Maximum distance to nearest park: 1,499.76 m

Mean distance to nearest park: 469.95 m


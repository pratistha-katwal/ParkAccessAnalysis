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

### Install Dependencies
poetry install


### Activate the environment
poetry env activate

### Running Main file
python NA_main.py

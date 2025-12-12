# NASA Power Downloader for QGIS

**Download NASA POWER daily climate data directly inside QGIS — no API key, no hassle.**

Perfect for agriculture, renewable energy, hydrology, and climate research — especially in Africa and the Global South.

[![QGIS Plugin](https://img.shields.io/badge/QGIS-Plugin-brightgreen.svg)](https://plugins.qgis.org/plugins/nasa_power_downloader/)
[![Version](https://img.shields.io/badge/Version-1.0.0-blue.svg)](https://plugins.qgis.org/plugins/nasa_power_downloader/)
[![QGIS ≥ 3.30](https://img.shields.io/badge/QGIS-≥3.30-orange.svg)]()
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://www.gnu.org/licenses/gpl-3.0)

![NASA Power Downloader Screenshot](https://raw.githubusercontent.com/wisekely/nasa-power-downloader/main/screenshot.png)

## Features

- Single point or bounding box (area) download
- Live red marker / red box preview on the moment you type coordinates
- Opens with full Africa view + OpenStreetMap background by default
- 12 most-used NASA POWER parameters (precipitation, temperature, humidity, solar, wind, etc.)
- 4 output formats: CSV • JSON • NetCDF (auto-loaded as raster) • ICASA
- Date range selection (1981 – near real-time)
- "Use current map extent" button
- Progress bar + clear success messages
- No registration, no API key required

## Installation

1. In QGIS → **Plugins → Manage and Install Plugins…**
2. Go to **All** tab → search **search**: `NASA Power`
3. Click **Install Plugin**

Or download manually from the official repository:  
https://plugins.qgis.org/plugins/nasa_power_downloader/

## 🎥 Video Tutorial
[![Watch the video](https://img.youtube.com/vi/X7XEv1E62aI/0.jpg)](https://youtu.be/X7XEv1E62aI)

**Watch the full tutorial here:** https://youtu.be/X7XEv1E62aI

## Quick Usage

1. Open the plugin: **Web → NASA Power Downloader**
2. Choose **Single Point** (default) or click on map) or **Area**
3. Select parameters and date range
4. Choose output format
5. Click **Download**

→ CSV/JSON opens in your browser, NetCDF loads automatically as raster layer in QGIS.

## Parameters Included

| Code                 | Description                          |
|----------------------|--------------------------------------|
| PRECTOT              | Precipitation                        |
| T2M                  | Temperature at 2m                    |
| T2M_MAX / T2M_MIN    | Daily max/min temperature            |
| RH2M                 | Relative humidity at 2m              |
| WS2M                 | Wind speed at 2m                         |
| WD2M                 | Wind direction at 2m                 |
| ALLSKY_SFC_SW_DWN    | All-sky surface shortwave down       |
| CLRSKY_SFC_SW_DWN    | Clear-sky surface shortwave down     |
| QV2M                 | Specific humidity                    |
| PS                   | Surface pressure                     |
| T2MDEW               | Dew/frost point temperature          |

More parameters coming in future versions!

## Author & Contact

**Wise Kely**  
Email: wisekely@gmail.com  
Twitter/X: @wisekely 

LinkedIn: (https://www.linkedin.com/in/wiseman-kelonye-21a30933/)

## License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

## Thank You!

This plugin is already helping researchers, farmers, and renewable energy planners across Africa and beyond.

Star this repo if you found it useful — it means the world!

Made with love for the Kenyan GIS community and the entire QGIS world.

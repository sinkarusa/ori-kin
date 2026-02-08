# ORI-KIN Pattern Generator

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)

A web application for generating Pseudo-Dome and Barrel Vault patterns with customizable parameters. This tool helps create precise geometric patterns for architectural and design purposes. These patterns were developed by Andrée Sonad Karaveli Kartal ([askk-arch.com.tr](https://askk-arch.com.tr)) for her thesis (located in docs).

## Features

- Interactive, custimaziable Pseudo-Dome and Barrel Vault pattern generators
- Export to SVG and DXF formats
- Real-time visualization
- Detailed parameter calculations
- TypeScript/JavaScript implementation for browser-based usage (`web-app/`)

## Demo

You can demo the app here: https://ori-kin.onrender.com/

### Demo Usage

**Pattern Generation**
* Select a pattern
* Adjust parameters
* Export SVG

**Pattern Visualization**
* Go to [Origami Simulator by Amanda Ghassaei](https://origamisimulator.org/)
* **File** -> **Import** and Select the exported SVG
* When prompted for **Vertex merge tolerance (px)**, enter a value `~0.1` (if using default pattern generation scale parameters, may need to tweak)
* You can visualize the pattern in 3D while Folding it

## Installation

### Prerequisites

- Python 3.11+
- Poetry

### Setup

```bash
# Clone the repository
git clone https://github.com/sinkarusa/ori-kin.git
cd ori-kin

# Install dependencies using Poetry
poetry install

# Activate the virtual environment
poetry shell
```

## Usage

### Development Server

```bash
python run.py
```

Visit `http://localhost:8050` in your web browser.

### Production Deployment

The application is configured for deployment on Render.com using Poetry and Gunicorn.


## Export Options

### SVG Export
- Vector graphics suitable for design software
- Maintains pattern precision
- Web-friendly format
- Readily uploadable to `https://origamisimulator.org/` for 3D visualization of the folding

### DXF Export
- CAD-compatible format
- Precise measurements
- Suitable for manufacturing

## License
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

This project is licensed under the GNU General Public License v3.0 - see the [COPYING](COPYING) file for details.

Copyright (C) [2024-2025] [Andrée Sonad Karaveli Kartal](https://askk-arch.com.tr), [Sinan Karaveli](https://github.com/sinkarusa)





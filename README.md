# Pseudo-Dome Pattern Generator

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)

A web application for generating pseudo-dome patterns with customizable parameters. This tool helps create precise geometric patterns for architectural and design purposes.

## Features

- Interactive pattern generation
- Customizable parameters (radius, segments, colors)
- Export to SVG and DXF formats
- Real-time visualization
- Detailed parameter calculations

## Installation

### Prerequisites

- Python 3.9+
- Poetry

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/pseudo-dome.git
cd pseudo-dome

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

## Configuration

Adjust parameters in the web interface:
- Radius (r)
- Number of segments (n)
- Colors for different fold types
- Line widths

## Export Options

### SVG Export
- Vector graphics suitable for design software
- Maintains pattern precision
- Web-friendly format

### DXF Export
- CAD-compatible format
- Precise measurements
- Suitable for manufacturing

## License

This project is licensed under the GNU General Public License v3.0 - see the [COPYING](COPYING) file for details.

Copyright (C) [2024] [Andrée Sonad Karaveli Kartal] [Sinan Karaveli]

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Acknowledgments

- [Dash](https://dash.plotly.com/) for the web framework
- [Plotly](https://plotly.com/) for visualization
- [ezdxf](https://ezdxf.mozman.at/) for DXF export capabilities

### Directory structure:
```
├── app/
│   ├── __init__.py                 # App factory and initialization
│   ├── callbacks.py                # Dash callback functions
│   ├── config.py                   # Configuration variables and constants
│   ├── layout.py                   # Dash layout definition
│   └── utils/
│       ├── __init__.py             # Exports main utility functions
│       ├── calculations.py         # Mathematical calculations
│       ├── export.py               # SVG and DXF export functionality
│       └── pattern_generator.py    # Pattern generation logic
├── COPYING                         # License 
├── gunicorn_config.py              # Gunicorn server configuration
├── poetry.lock                     # Poetry dependency lock file
├── pyproject.toml                  # Poetry project and dependency configuration
├── README.md                       # Readme
├── run.py                          # Development server script
└── wsgi.py                         # WSGI application entry point for production
```

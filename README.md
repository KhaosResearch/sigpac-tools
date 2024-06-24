# [SIGPAC-Tools](https://github.com/KhaosResearch/sigpac-tools)

![Python >=3.10](https://img.shields.io/badge/python-%3E=3.10-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Status: Active](https://img.shields.io/badge/Status-Active-00aa00.svg)
![Code style: Ruff](https://img.shields.io/badge/code%20style-Ruff-aa0000.svg)


SIGPAC-Tools is a Python library that provides the user a set of tools to work with the SIGPAC data. The library is designed to be easy to use and to provide the user the ability to work with the data in a simple way.

This library is designed to be used in conjunction with the SIGPAC data provided by the Spanish government. The data is available in the [SIGPAC website](https://sigpac.mapa.gob.es/fega/visor/).

## Installation

To install the library, you can use the following command:

```bash
git clone https://github.com/KhaosResearch/sigpac-tools
python -m pip install ./sigpac-tools
```

or you can install it directly from the repository:

```bash
python -m pip install https://github.com/KhaosResearch/sigpac-tools
```

## Usage

Once the library is installed, you can use it in your Python code. The library provides a set of tools to work with the SIGPAC data, these are the main features:

### Search for an specific plot

You can search for an specific plot using the `search` function in the `search` module. This function will return a list of plots that match the search criteria.

```python
from sigpac_tools.search import search

data = {
    "community": 1,
    "province": 1,
    "municipality": 8,
    "polygon": 8,
    "parcel": 572
}

geojson = search(data)
```

It is important to note that the `search` function will return a GeoJSON object with the information of the plots that match the search criteria. The `data` dictionary must contain at least the 'province' or the 'community' key to return a valid result. Note that all the keys must be in lower case.

### Get the information of a plot

You can get the information of a plot using the `get_metadata` function in the `anotate` module. This function will return a dictionary with the information of the plot, given the same data as the `search` function.

```python
from sigpac_tools.anotate import get_metadata

layer = "parcela"
data = {
    "community": 1,
    "province": 1,
    "municipality": 8,
    "polygon": 8,
    "parcel": 572,
    # "enclosure": 1,
    # "aggregate": 0,
    # "zone": 0
}

metadata = get_metadata(
    layer,
    data
)
```

> `enclosure` is only necesary if the layer is "recinto". `aggregate` and `zone` are optional and depend on the location of the parcel or enclosure searched for.

### Get the geometry of a plot

Given the coordinates of the plot, that may be gathered from the function `search`, you can get the geometry of the plot using the `geometry_from_coords` function in the `locate` module. This function will return a GeoJSON object with the geometry of the plot. 

The user may specify a reference parcel or enclosure to get the geometry of and so on the function will return the geometry of that specific parcel or enclosure if it exists. If the reference parcel or enclosure does not exist, the function will return `None`.

If the reference parcel or enclosure is not provided, the function will return a Feature Collection with all the parcels that match the search criteria.

```python
from sigpac_tools.locate import geometry_from_coords

layer = "parcela"
lat = 37.384 
lng = -4.98
reference = None

geometry = geometry_from_coords(
    layer,
    lat,
    lng,
    reference
)
```

## Acknowledgements

This inspired by the JavaScript [SIGPAC client](https://github.com/dan96ct/sigpac-client) made by Daniel Cebrián.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright 2023 Khaos Research, all rights reserved.
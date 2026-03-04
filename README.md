# [SIGPAC-Tools](https://github.com/KhaosResearch/sigpac-tools)

![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FKhaosResearch%2Fsigpac-tools%2Fmain%2Fpyproject.toml)
 [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
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
python -m pip install git+https://github.com/KhaosResearch/sigpac-tools
```

## Usage

Once the library is installed, you can use it in your Python code. The library provides a set of tools to work with the SIGPAC data, these are the main features:

### Get plot information from cadastral data

You can get the information of a plot using the `get_geometry_and_metadata_cadastral` function in the `anotate` module. This function will return a tuple of dictionaries with the geometry and metadata of the plot, given the cadastral data search criteria.

```python
from sigpac_tools.anotate import get_geometry_and_metadata_cadastral

layer = "parcela"

province= 14
municipality= 48
polygon= 1
parcel= 199
# enclosure= 1
# aggregate= 0
# zone= 0

metadata, geometry = get_geometry_and_metadata_cadastral(
    layer,province, municipality, polygon, parcel
)
```

> `enclosure` is only necesary if the `layer` is "recinto". `aggregate` and `zone` are optional and depend on the location of the parcel or enclosure searched for.

### Get plot information from plot coordinates

You can also get the geometry and metadata of the plot using the `get_geometry_and_metadata_coords` function in the `locate` module. This function will return a both the GeoJSON object with the geometry of the plot and the metadata dictionary. 

The user can specify whether to retrieve the information on a single enclosure inside the plot or the whole parcel associated to the coordinates using the `layer` argument.

```python
from sigpac_tools.locate import get_geometry_and_metadata_coords

layer = "parcela"
lat = 37.265840
lng = -4.593406 

geometry, metadata = get_geometry_and_metadata_coords(
    layer,
    lat,
    lng,
    # crs="4258"
)
```
> Default value for `crs` is already set, but users may change it if the they need it.

### Get plot information from a specific cadastral registry

Known a cadastral registry, you can get the polygon and metadata from it using the `find_from_cadastral_registry` from the module `find`. 
This function will return a tuple with a GeoJSON object of the polygon and a dictionary with the metadata of the plot. It will only return the metadata of the "parcela" layer.

Note that **urban cadastral registries are not supported yet**, due to the lack of information about them in the SIGPAC database.

If an invalid cadastral registry is provided, the function will raise a `ValueError`. If it detects that the cadastral registry is urban, it will raise a `NotImplementedError`.

An example of how to use this function is shown below:

```python
from sigpac_tools.find import find_from_cadastral_registry

cadastral_registry = "14048A001001990000RM"
geometry, metadata = find_from_cadastral_registry(cadastral_registry)
```
### Generate synthetic Sigpac cadastral registry
Provided with some cadastral data, a synthetic rural cadastral registry can be generated using the `buidl_cadastral_reference` from the `generate` module. This registry will be valid within the scope of the `find_from_cadastral_registry` method. It cannot be used against any official SIGPAC database.
```python
from sigpac_tools.generate import build_cadastral_reference

prov = 14,
muni = 48,
poly = 1,
parcel = 199,
# encl = 0
# section = 'A'

syn_cadastral_ref = build_cadastral_reference(prov, muni, poly, parcel)

geometry, metadata = find_from_cadastral_registry(syn_cadastral_ref)
```

## Acknowledgements

This project was inspired by the JavaScript [SIGPAC client](https://github.com/dan96ct/sigpac-client) made by Daniel Cebrián.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright 2024 Khaos Research, all rights reserved.

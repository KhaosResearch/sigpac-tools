import structlog

from sigpac_tools.search import search
from sigpac_tools.anotate import get_metadata
from sigpac_tools.locate import geometry_from_coords
from sigpac_tools.utils import read_cadastral_registry


logger = structlog.get_logger()


def find_from_cadastral_registry(cadastral_reg: str):
    """
    Find the geometry and metadata of a cadastral reference in the SIGPAC database. The reference must be rural. Urban references are not supported.

    The expected cadastral registry is a 20 character string with the following format:

    - 2 characters for the province
    - 3 characters for the municipality
    - 1 character for the section
    - 3 characters for the polygon
    - 5 characters for the parcel
    - 4 characters for the id
    - 2 characters for the control
    Parameters
    ----------
    cadastral_reg : str
        Cadastral reference to search for

    Returns
    -------
    dict
        Geojson geometry of the found reference
    dict
        Metadata of the found reference

    Raises
    -------
    ValueError
        If the cadastral reference does not exist in the SIGPAC database
    ValueError
        If the length of the cadastral reference is not 20 characters
    ValueError
        If the province of the cadastral reference is not valid
    ValueError
        If the reference is not valid
    NotImplementedError
        If the reference is urban
    """
    reg = read_cadastral_registry(cadastral_reg)

    # Search for coordinates

    search_data = search(reg)
    if search_data["features"] == []:
        raise ValueError(
            f"The cadastral reference {cadastral_reg} does not exist in the SIGPAC database. Please check the if the reference is correct and try again. Urban references are not supported."
        )

    coords_x = []
    coords_y = []
    for feat in search_data["features"]:
        coords_x.append((feat["properties"]["x1"] + feat["properties"]["x2"]) / 2)
        coords_y.append((feat["properties"]["y1"] + feat["properties"]["y2"]) / 2)
    coords = [sum(coords_x) / len(coords_x), sum(coords_y) / len(coords_y)]

    # Get geometry

    geometry = geometry_from_coords(
        layer="parcela", lat=coords[1], lon=coords[0], reference=reg["parcel"]
    )

    # Get metadata

    metadata = get_metadata(layer="parcela", data=reg)

    return geometry, metadata

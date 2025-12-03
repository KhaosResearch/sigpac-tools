import requests
import structlog

from sigpac_tools._globals import BASE_URL, QUERY_URL
from sigpac_tools.anotate import extract_geometry, extract_metadata, get_geometry_and_metadata_cadastral

logger = structlog.get_logger()


def get_geometry_and_metadata_coords(layer: str, lat: float, lon: float, crs: str = "4258") -> dict:
    """Gets the geometry of the given coordinates and reference in the given layer

    Parameters
    ----------
    layer : str
        Layer to search from ("parcela", "recinto")
    lat : float
        Latitude of the location
    lon : float
        Longitude of the location
    crs : str
        Coordinates reference system

    Returns
    -------
    dict, dict
        Geojson geometry and metadata of the found reference

    Raises
    ------
    ValueError
        If the layer, latitude, longitude or reference is not specified
    KeyError
        If the layer is not supported
    """
    if not layer or not lat or not lon:
        raise ValueError("Layer, latitude or longitude not specified")

    url = f"{BASE_URL}/{QUERY_URL}/recinfobypoint/{crs}/{lon}/{lat}.geojson"
    logger.debug(f"SIGPAC endpoint: {url}")
    response = requests.get(url)
    features_and_metadata = response.json()

    if layer == "parcela":
        logger.info(f"Searching for all enclosures' data in the layer {layer}...")
        # Make additional SIGPAC API call to get all of the parcel's data
        reference_data = features_and_metadata.get("features")[0].get("properties")
        data = {
            "province": int(reference_data.get("provincia")),
            "municipality": int(reference_data.get("municipio")),
            "polygon": int(reference_data.get("poligono")),
            "parcel": int(reference_data.get("parcela")),
        }
        geometry, metadata = get_geometry_and_metadata_cadastral(layer, data)

    elif layer == "recinto":
        logger.info(f"Searching for enclosure's data in the layer {layer}...")
        geometry = extract_geometry(features_and_metadata,)
        metadata = extract_metadata(features_and_metadata, layer)
    else:
        raise KeyError(
            f'Layer "{layer}" not supported. Supported layers: "parcela", "recinto"'
        )

    return geometry, metadata

if __name__ == '__main__':

    layer = "parcela"
    lat = 37.265840
    lng = -4.593406 
    reference = None

    geometry, metadata = get_geometry_and_metadata_coords(
        layer,
        lat,
        lng
    )
    logger.debug(f"METADATA:\n\n{str(metadata)[:500]}\n...\n\n")
    logger.debug(f"GEOMETRY:\n\n{str(geometry)[:500]}\n...\n\n")

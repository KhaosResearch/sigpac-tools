import requests
import structlog

from sigpac_tools._globals import BASE_URL
from sigpac_tools.utils import lng_lat_to_tile, transform_coords

logger = structlog.get_logger()


def __locate_in_feature_collection(
    reference: int, layer: str, featureCollection: dict
) -> dict | None:
    """Locates the given reference in the feature collection given the layer to search from

    Parameters
    ----------
    reference : int
        Reference to search
    layer : str
        Layer to search from ("parcela", "recinto")
    featureCollection : dict
        Geojson feature collection to search from

    Returns:
    dict | None
        Geojson geometry of the found reference. If not found, returns `None`
    """
    for feature in featureCollection["features"]:
        if feature["properties"][layer] == reference:
            projection = "epsg:4326"
            transform_coords(feature, "epsg:4326")
            geom = feature["geometry"]
            geom["CRS"] = projection
            return geom
    return None


def geometry_from_coords(layer: str, lat: float, lon: float, reference: int) -> dict:
    """Gets the geometry of the given coordinates and reference in the given layer

    Parameters
    ----------
    layer : str
        Layer to search from ("parcela", "recinto")
    lat : float
        Latitude of the location
    lon : float
        Longitude of the location
    reference : int
        Reference to search for

    Returns
    -------
    dict
        Geojson geometry of the found reference

    Raises
    ------
    ValueError
        If the layer, latitude, longitude or reference is not specified
    KeyError
        If the layer is not supported
    """
    if not layer or not lat or not lon:
        raise ValueError("Layer, latitude or longitude not specified")

    tile_x, tile_y = lng_lat_to_tile(lon, lat, 15)

    response = requests.get(
        f"{BASE_URL}/vectorsdg/vector/{layer}@3857/15.{tile_x}.{tile_y}.geojson"
    )

    geojson_features = response.json()

    if not reference:
        logger.info(
            f"No reference specified. Returning all features in the layer {layer} for coordinates ({lat}, {lon})"
        )
        return geojson_features

    if layer in ["parcela", "recinto"]:
        logger.info(f"Searching for reference {reference} in the layer {layer}...")
        result = __locate_in_feature_collection(
            reference=reference, layer=layer, featureCollection=geojson_features
        )
        if not result:
            logger.warning(
                f"Reference '{reference}' not found in the layer '{layer}' at coordinates ({lat}, {lon})"
            )
        else:
            logger.info(
                f"Reference '{reference}' found in the layer '{layer}' at coordinates ({lat}, {lon})"
            )
        return result

    else:
        raise KeyError(
            f'Layer "{layer}" not supported. Supported layers: "parcela", "recinto"'
        )

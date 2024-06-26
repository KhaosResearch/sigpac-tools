import requests
import structlog

from sigpac_tools._globals import BASE_URL

logger = structlog.get_logger()


def __query(
    layer: str,
    province: int,
    municipality: int,
    polygon: int,
    parcel: int,
    enclosure: int,
    aggregate: int,
    zone: int,
) -> dict:
    """Queries the SIGPAC database for the given location parameters and layer

    Parameters
    ----------
    layer : str
        Layer to search from ("parcela", "recinto")
    province : int
        Province code
    municipality : int
        Municipality code
    polygon : int
        Polygon code
    parcel : int
        Parcel code
    enclosure : int
        Enclosure code
    aggregate : int
        Aggregate code
    zone : int
        Zone code

    Returns
    -------
    dict
        Dictionary with the metadata of the SIGPAC database

    Raises
    ------
    KeyError
        If the layer is not supported
    """
    match layer.lower():
        case "parcela":
            logger.info("Searching for the parcel specified")
            url = f"{BASE_URL}/fega/ServiciosVisorSigpac/LayerInfo"
            params = {
                "layer": layer,
                "id": f"{province},{municipality},{aggregate},{zone},{polygon},{parcel}",
            }
            response = requests.get(url, params=params)
            return response.json()
        case "recinto":
            logger.info("Searching for the enclosure specified")
            url = f"{BASE_URL}/fega/ServiciosVisorSigpac/LayerInfo"
            params = {
                "layer": layer,
                "id": f"{province},{municipality},{aggregate},{zone},{polygon},{parcel},{enclosure}",
            }
            response = requests.get(url, params=params)
            return response.json()
        case _:
            raise KeyError(
                "Layer not supported. Supported layers: ['parcela', 'recinto']"
            )


def get_metadata(layer: str, data: dict):
    """Get the metadata of the given location from the SIGPAC database

    It searches for the metadata of the given location in the SIGPAC database. The search can be done by specifying the layer, province, municipality, polygon and parcel.
    The level of detail of the search can be increased by specifying the layer to search between "parcela" and "recinto".

    Parameters
    ----------
    layer : str
        Layer to search from ("parcela", "recinto")
    data : dict
        Dictionary with the data of the location to search. It must be a dictionary with the following keys: [ province, municipality, aggregate, zone, polygon, parcel ]

    Returns
    -------
    dict
        Dictionary with the metadata of the SIGPAC database

    Raises
    ------
    ValueError
        If the layer, province, municipality, polygon or parcel is not specified
    KeyError
        If the layer is not supported
    """
    if not layer:
        raise ValueError("Layer not specified")
    elif layer not in ["parcela", "recinto"]:
        raise KeyError("Layer not supported. Supported layers: ['parcela', 'recinto']")

    prov = data.get("province", None)
    muni = data.get("municipality", None)
    polg = data.get("polygon", None)
    parc = data.get("parcel", None)
    encl = data.get("enclosure", None)
    aggr = data.get("aggregate", 0)
    zone = data.get("zone", 0)

    if not prov:
        raise ValueError("Province not specified")
    if not muni:
        raise ValueError("Municipality not specified")
    if not polg:
        raise ValueError("Polygon not specified")
    if not parc:
        raise ValueError("Parcel not specified")
    if not encl and layer == "recinto":
        raise ValueError("Enclosure not specified")

    logger.info(
        f"Searching for the metadata of the location (province {prov}, municipality {muni}, polygon {polg}, parcel {parc}) in the SIGPAC database..."
    )

    res = __query(
        layer=layer,
        province=prov,
        municipality=muni,
        polygon=polg,
        parcel=parc,
        enclosure=encl,
        aggregate=aggr,
        zone=zone,
    )
    if res is None:
        raise ValueError(
            f"The location (province {prov}, municipality {muni}, polygon {polg}, parcel {parc}) does not exist in the SIGPAC database. Please check the data and try again."
        )
    else:
        logger.info(
            f"Metadata of the location (province {prov}, municipality {muni}, polygon {polg}, parcel {parc}{f', enclosure {encl}' if layer == 'recinto' else ''}) found in the SIGPAC database."
        )
    return res

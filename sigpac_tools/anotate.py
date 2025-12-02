from collections import defaultdict
import requests
import structlog

from sigpac_tools._globals import BASE_URL, QUERY_URL

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
    id = ""
    match layer.lower():
        case "parcela":
            logger.info("Searching for the parcel specified")
            id = f"recinfoparc/{province}/{municipality}/{aggregate}/{zone}/{polygon}/{parcel}"
        case "recinto":
            logger.info("Searching for the enclosure specified")
            id = f"recinfo/{province}/{municipality}/{aggregate}/{zone}/{polygon}/{parcel}/{enclosure}"
        case _:
            raise KeyError(
                "Layer not supported. Supported layers: ['parcela', 'recinto']"
            )
    
    url = f"{BASE_URL}/{QUERY_URL}/{id}.geojson"
    logger.debug(f"SIGPAC endpoint: {url}")
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


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

    comm = data.get("community", None)
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
    
    province_code = int(str(comm+prov))

    res = __query(
        layer=layer,
        province=province_code,
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
    
    metadata = extract_metadata(res)
    
    return metadata

def extract_metadata(response_json: dict) -> dict:
    """Extract parcel metadata from SIGPAC data response.

    Parameters:
    ----------
        response_json (dict): All parcel's enclousure info JSON data

    Returns:
    -------
        full_parcel_metadata (dict): JSON metadata for the overall parcel

    Raises
    -------
        ValueError: If no data was found

    """

    # Prepare outputs
    query = []
    land_use = []
    total_surface = 0.0

    for feature in response_json.get("features", []):
        properties = feature.get("properties", {})

        # Extract and enrich info
        dn_surface = properties.get("superficie")
        uso_sigpac = properties.get("uso_sigpac")
        superficie_admisible = dn_surface
        inctexto = None

        # Query info
        query_cols = ["admisibilidad", "altitud", "coef_regadio", "incidencias",
                      "pendiente_media", "recinto", "region", "uso_sigpac"]
        query_entry = {col: properties.get(col) for col in query_cols}
        query_entry.update({
            "dn_surface": superficie_admisible,
            "inctexto": inctexto,
            "superficie_admisible": superficie_admisible,
            "uso_sigpac": uso_sigpac
        })

        # Land use info
        land_use_entry = {
            "dn_superficie": dn_surface,
            "superficie_admisible": dn_surface,
            "uso_sigpac": properties.get("uso_sigpac")
        }

        # Append to lists
        query.append(query_entry)
        land_use.append(land_use_entry)

        # Add surface to total parcel surface
        total_surface += dn_surface

    # Parcel info
    parcel_info_cols = ["provincia", "municipio",
                        "agregado", "poligono", "parcela"]
    parcel_info_entry = {col: properties.get(col) for col in parcel_info_cols}
    parcel_info_entry.update({
        "referencia_cat": "",
        "dn_surface": total_surface
    })

    # --- GROUP LAND USES ---
    land_use_summary = defaultdict(float)
    for entry in land_use:
        uso = entry.get("uso_sigpac")
        if uso:
            land_use_summary[uso] += float(entry.get("dn_superficie", 0.0))

    # Convert back to list of dicts for output
    land_use_grouped = [
        {"uso_sigpac": uso, "dn_superficie": round(
            area, 4), "superficie_admisible": round(area, 4)}
        for uso, area in land_use_summary.items()
    ]

    # Build final parcel metadata
    full_parcel_metadata = {
        "arboles": None,
        "convergencia": None,
        "id": None,
        "isRecin": None,
        "parcelaInfo": parcel_info_entry,
        "query": query,
        "usos": land_use_grouped,
        "vigencia": None,
        "vuelo": None
    }
    logger.info("Extracted metadata successfully.")

    return full_parcel_metadata


if __name__ == '__main__':

    layer = "parcela"
    data = {
        "community": 2,
        "province": 6,
        "municipality": 2,
        "polygon": 1,
        "parcel": 1,
        # "enclosure": 2,
        # "aggregate": 0,
        # "zone": 0
    }

    metadata = get_metadata(
        layer,
        data
    )
    logger.debug(f"METADATA:\n\n{metadata}\n\n")

import requests
import structlog

from collections import defaultdict
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

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
            logger.info("Searching for the specified parcel")
            id = f"recinfoparc/{province}/{municipality}/{aggregate}/{zone}/{polygon}/{parcel}"
        case "recinto":
            logger.info("Searching for the specified enclosure")
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

def get_geometry_and_metadata(layer: str, data: dict):
    """Get the metadata of the given location from the SIGPAC database

    The search can be done by specifying the layer, province, municipality, polygon and parcel.
    The level of detail of the search can be increased by specifying the layer to search between "parcela" and "recinto".

    Parameters
    ----------
    layer : str
        Layer to search from ("parcela", "recinto")
    data : dict
        Dictionary with the data of the location to search. It must be a dictionary with the following keys: [ province, municipality, aggregate, zone, polygon, parcel ]

    Returns
    -------
    dict, dict
        Dictionaries with the metadata and geometry of the SIGPAC database

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
        f"Searching for the data of the location (province {prov}, municipality {muni}, polygon {polg}, parcel {parc}) in the SIGPAC database..."
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
            f"Data of the location (province {prov}, municipality {muni}, polygon {polg}, parcel {parc}{f', enclosure {encl}' if layer == 'recinto' else ''}) found in the SIGPAC database."
        )
    
    geometry = extract_geometry(res)
    metadata = extract_metadata(res, layer)
    
    return geometry, metadata

def extract_geometry(full_json: dict) -> dict:
    """ Extract parcel geometry info from all of the individual enclosures geometry data.

    Parameters
    ----------
    full_json (dict):
        All parcel's enclousure info JSON data

    Returns
    -------
    full_parcel_geometry (dict):
        GeoJSON for overall parcel geometry

    Raises
    -------
        ValueError: If no geometries were found
    """
    full_parcel_geometry = {}

    # Extract all geometries from features
    all_geometries = [shape(feature["geometry"])
                      for feature in full_json["features"]]

    if not all_geometries:
        raise ValueError("No geometries found in the provided JSON data.")

    logger.info("Found full metadata and geometry info for parcel.")

    # Merge all geometries into one (union of polygons)
    merged_geometry = unary_union(all_geometries)

    # Convert back to GeoJSON format
    full_parcel_geometry = mapping(merged_geometry)

    # Add CRS
    crs = f'{str(full_json["crs"]["type"]).lower()}:{full_json["crs"]["properties"]["code"]}'
    full_parcel_geometry['CRS'] = crs
    logger.info("Extracted geometry successfully.")

    return full_parcel_geometry

def extract_metadata(response_json: dict, layer: str) -> dict:
    """Extract parcel metadata from SIGPAC data response

    Parameters
    ----------
    response_json : dict 
        All parcel's enclousure info JSON data
    layer : str
        Layer to search from ("parcela", "recinto")

    Returns
    -------
    full_parcel_metadata : dict
        JSON metadata for the overall parcel

    Raises
    -------
    ValueError: If no data was found

    """

    # Prepare outputs
    query = []
    land_use = []
    total_surface = 0.0

    features = response_json.get("features", [])

    for feature in features:
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
    if len(features) < 2:
        parcel_info_cols.append("zona")
        parcel_info_cols.append("recinto")

    parcel_info_entry = {col: properties.get(col) for col in parcel_info_cols}
    parcel_info_entry.update({
        # "referencia_cat": "",
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
        # "arboles": None,
        # "convergencia": None,
        # "id": None,
        "isRecin": layer == "recinto",
        "parcelaInfo": parcel_info_entry,
        "query": query,
        "usos": land_use_grouped,
        # "vigencia": None,
        # "vuelo": None
    }
    logger.info("Extracted metadata successfully.")

    return full_parcel_metadata

if __name__ == '__main__':

    layer = "parcela"
    data = {
        "province": 26,
        "municipality": 2,
        "polygon": 1,
        "parcel": 1,
        # "enclosure": 2,
        # "aggregate": 0,
        # "zone": 0
    }

    metadata, geometry = get_geometry_and_metadata(
        layer,
        data
    )
    logger.debug(f"METADATA:\n\n{str(metadata)[:500]}\n...\n\n")
    logger.debug(f"GEOMETRY:\n\n{str(geometry)[:500]}\n...\n\n")

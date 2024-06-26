import requests
import structlog

from sigpac_tools._globals import BASE_URL
from sigpac_tools.utils import find_community

logger = structlog.get_logger()


def search(data: dict) -> dict:
    """Search for a specific location in the SIGPAC database

    Search for the information of the given location in the SIGPAC database. The search can be done by specifying the community, province, municipality, polygon and parcel.

    Parameters
    ----------
    data : dict
        Dictionary with the data of the location to search. It must be a dictionary with the following keys: [ community, province, municipality, polygon, parcel ]

    Returns
    -------
    dict
        Dictionary with information about the location searched and the coordinates of the polygon or parcels

    Raises
    ------
    ValueError
        If the community is not specified and it is required to search for the location
    """
    comm = data.get("community", None)
    prov = data.get("province", None)
    muni = data.get("municipality", None)
    polg = data.get("polygon", None)
    parc = data.get("parcel", None)

    if not comm:
        if not prov:
            raise ValueError(
                '"Community" has not been specified, neither has been "province" and it is compulsory to find the community associated'
            )
        else:
            comm = find_community(prov)

    if comm:
        if prov:
            if muni:
                if polg:
                    if parc:
                        logger.info("Searching for the parcel specified")
                        response = requests.get(
                            f"{BASE_URL}/fega/ServiciosVisorSigpac/query/recintos/{prov}/{muni}/0/0/{polg}/{parc}.geojson"
                        )
                        geojson = response.json()
                        return geojson
                    else:
                        logger.info(f"Searching for the parcels of the polygon {polg}")
                        response = requests.get(
                            f"{BASE_URL}/fega/ServiciosVisorSigpac/query/parcelas/{prov}/{muni}/0/0/{polg}.geojson"
                        )
                        geojson = response.json()
                        return geojson
                else:
                    logger.info(
                        f"Searching for the polygons of the municipality {muni}"
                    )
                    response = requests.get(
                        f"{BASE_URL}/fega/ServiciosVisorSigpac/query/poligonos/{prov}/{muni}/0/0.geojson"
                    )
                    geojson = response.json()
                    return geojson
            else:
                logger.info(f"Searching for the municipalities of the province {prov}")
                response = requests.get(
                    f"{BASE_URL}/fega/ServiciosVisorSigpac/query/municipios/{prov}.geojson"
                )
                geojson = response.json()
                return geojson
        else:
            logger.info(f"Searching for the provinces of the community {comm}")
            response = requests.get(
                f"{BASE_URL}/fega/ServiciosVisorSigpac/query/provincias/{comm}.geojson"
            )
            geojson = response.json()
            return geojson

    else:
        raise ValueError(
            '"Community" has not been specified and it could have not been found from the "province" parameter'
        )

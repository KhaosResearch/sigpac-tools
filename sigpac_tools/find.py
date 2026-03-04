import structlog

from sigpac_tools.anotate import get_geometry_and_metadata_cadastral
from sigpac_tools.utils import read_cadastral_registry


logger = structlog.get_logger()


def find_from_cadastral_registry(cadastral_ref: str):
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
    reg = read_cadastral_registry(cadastral_ref)
    
    province= reg.get("province")
    municipality= reg.get("municipality")
    polygon= reg.get("polygon")
    parcel= reg.get("parcel")
    enclosure= reg.get("id_inm")

    layer = "recinto" if enclosure else "parcela"

    # Search for coordinates

    geometry, metadata = get_geometry_and_metadata_cadastral(
        layer, province, municipality, polygon, parcel, enclosure
    )

    return geometry, metadata


if __name__ == '__main__':
    cadastral_reference = '14048A001001990000RM'

    geometry, metadata = find_from_cadastral_registry(cadastral_reference)

    logger.debug(f"METADATA:\n\n{str(metadata)[:500]}\n...\n\n")
    logger.debug(f"GEOMETRY:\n\n{str(geometry)[:500]}\n...\n\n")

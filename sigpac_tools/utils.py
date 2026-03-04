import math
import pyproj
import structlog

from sigpac_tools._globals import PROVINCES_BY_COMMUNITY

logger = structlog.get_logger()


def lng_lat_to_tile(lng: float, lat: float, zoom: float) -> tuple[int, int]:
    """Transforms the given coordinates from longitude and latitude to tile coordinates for the given zoom level"""

    ORIGIN_SHIFT = 2 * math.pi * 6378137 / 2.0
    TILESIZE = 256

    x = lng * ORIGIN_SHIFT / 180.0
    y = math.log(math.tan((90 + lat) * math.pi / 360.0)) / (math.pi / 180.0)
    y = y * ORIGIN_SHIFT / 180.0

    x = round(x, 1)
    y = round(y, 1)

    resolution = (2 * math.pi * 6378137 / TILESIZE) / (2**zoom)

    px = (x + ORIGIN_SHIFT) / resolution
    py = (y + ORIGIN_SHIFT) / resolution

    if zoom == 0:
        return 0, 0, 0

    tx = math.ceil(px / TILESIZE) - 1
    ty = math.ceil(py / TILESIZE) - 1

    if tx < 0:
        tx = 0
    if ty < 0:
        ty = 0

    return tx, ty


def transform_coords(feature: dict, projection_id: str = "EPSG:4326") -> None:
    """Transforms the coordinates of the given feature from EPSG:3857 to EPSG:4326

    Parameters
    ----------
    feature : dict
        Geojson feature to transform
    projection_id : str
        Target projection ID (default: EPSG:4326)

    Returns
    -------
    None
    """
    transformer = pyproj.Transformer.from_crs(
        "EPSG:3857", projection_id, always_xy=True
    )
    for coords in feature["geometry"]["coordinates"]:
        for coord in coords:
            coord[0], coord[1] = transformer.transform(coord[0], coord[1])


def find_community(province_id: int) -> int:
    """Finds the community of the given province id"""
    for comunidad, provincias in PROVINCES_BY_COMMUNITY.items():
        if province_id in provincias:
            return comunidad
    return None


# Keep old name for backwards compatibility
findCommunity = find_community


def read_cadastral_registry(registry: str) -> dict:
    """Read the cadastral reference, validates it and return its data as a dictionary."""
    registry = registry.upper().replace(" ", "")
    if len(registry) != 20:
        raise ValueError("The cadastral reference must have a length of 20 characters")

    reg_prov = registry[:2]
    reg_mun = registry[2:5]
    reg_sec = registry[5]
    reg_pol = registry[6:9]
    reg_par = registry[9:14]
    reg_id = registry[14:18]
    reg_control = registry[18:]

    validate_cadastral_registry(registry)

    if not find_community(int(reg_prov)):
        raise ValueError(
            "The province of the cadastral reference is not valid. Please check if it is a correct rural reference and try again."
        )

    return {
        "province": int(reg_prov),
        "municipality": int(reg_mun),
        "section": reg_sec,
        "polygon": int(reg_pol),
        "parcel": int(reg_par),
        "id_inm": int(reg_id),
        "control": reg_control,
    }


def validate_cadastral_registry(reference: str) -> None:
    """Validate the cadastral reference"""
    sum_pd1 = 0
    sum_sd2 = 0
    mixt1 = 0
    reference = reference.upper().replace(" ", "")
    pos = [13, 15, 12, 5, 4, 17, 9, 21, 3, 7, 1]
    res = "MQWERTYUIOPASDFGHJKLBZX"

    if len(reference) != 20:
        raise ValueError("The cadastral reference must have a length of 20 characters")
    else:
        separated_ref = list(reference)

        for i in range(7):
            if separated_ref[i].isdigit():
                sum_pd1 += pos[i] * (ord(separated_ref[i]) - 48)
            else:
                if ord(separated_ref[i]) > 78:
                    sum_pd1 += pos[i] * (ord(separated_ref[i]) - 63)
                else:
                    sum_pd1 += pos[i] * (ord(separated_ref[i]) - 64)

        for i in range(7):
            if separated_ref[i + 7].isdigit():
                sum_sd2 += pos[i] * (ord(separated_ref[i + 7]) - 48)
            else:
                if ord(separated_ref[i + 7]) > 78:
                    sum_sd2 += pos[i] * (ord(separated_ref[i + 7]) - 63)
                else:
                    sum_sd2 += pos[i] * (ord(separated_ref[i + 7]) - 64)

        for i in range(4):
            mixt1 += pos[i + 7] * (ord(separated_ref[i + 14]) - 48)

        code_pos1 = (sum_pd1 + mixt1) % 23
        code_pos2 = (sum_sd2 + mixt1) % 23
        code1 = res[code_pos1]
        code2 = res[code_pos2]

        typo = "URBAN" if separated_ref[5].isdigit() else "RURAL"

        if typo == "URBAN":
            raise NotImplementedError(
                "Urban cadastral references are not supported yet."
            )

        if code1 == separated_ref[18] and code2 == separated_ref[19]:
            logger.info(f"Reference {reference} ({typo}) is valid.")
        else:
            raise ValueError(
                f"Reference {reference} ({typo}) is not valid. Expected control characters: {code1}{code2}, but got {separated_ref[18]}{separated_ref[19]}."
            )
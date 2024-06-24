import math
import pyproj

from sigpac_tools._globals import PROVINCES_BY_COMMUNITY


def lng_lat_to_tile(lng: float, lat: float, zoom: float) -> tuple[int, int]:
    """Transforms the given coordinates from longitude and latitude to tile coordinates for the given zoom level

    Parameters
    ----------
    lng : float
        Longitude of the location
    lat : float
        Latitude of the location
    zoom : float
        Zoom level to get the tile coordinates
    
    Returns
    -------
    tuple[int, int]
        Returns a tuple with the x and y tile coordinates
    """
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


def transform_coords(feature: dict) -> None:
    """Transforms the coordinates of the given feature from EPSG:3857 to EPSG:4326

    Parameters
    ----------
    feature : dict
        Geojson feature to transform

    Returns
    -------
    None
    """
    for coords in feature["geometry"]["coordinates"]:
        for coord in coords:
            firstProjection = 'PROJCS["WGS 84 / Pseudo-Mercator",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Mercator_1SP"],PARAMETER["central_meridian",0],PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["X",EAST],AXIS["Y",NORTH],EXTENSION["PROJ4","+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs"],AUTHORITY["EPSG","3857"]]'
            secondProjection = pyproj.Proj("epsg:4326")
            optimus_prime = pyproj.Transformer.from_proj(
                firstProjection, secondProjection
            )
            coord[1], coord[0] = optimus_prime.transform(coord[0], coord[1])


def findCommunity(province_id: int) -> int:
    """Finds the community of the given province id

    Parameters
    ----------
    province_id : int
        Province id to search for

    Returns
    -------
    int
        Returns the community id of the given province id
    """
    for comunidad, provincias in PROVINCES_BY_COMMUNITY.items():
        if province_id in provincias:
            return comunidad
    return None

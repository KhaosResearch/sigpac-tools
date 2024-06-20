import requests
from pyproj import Proj, Transformer
import math

BASE_URL = "https://sigpac.mapama.gob.es"


def __findComunidad(provincia: int) -> int:
    COMUNIDAD_PROVINCIAS = {
        1: [4, 11, 14, 18, 21, 23, 29, 41],
        2: [22, 44, 50],
        3: [33],
        4: [7],
        5: [35, 38],
        6: [39],
        7: [5, 9, 24, 34, 37, 40, 42, 47, 49],
        8: [2, 13, 16, 19, 45],
        9: [8, 17, 25, 43],
        10: [3, 12, 46],
        11: [6, 10],
        12: [15, 27, 32, 36],
        13: [28],
        14: [30],
        15: [31],
        16: [1, 20, 48],
        17: [26],
        18: [51],
        19: [52],
    }
    for comunidad, provincias in COMUNIDAD_PROVINCIAS.items():
        if provincia in provincias:
            return comunidad
    return None


def __lng_lat_to_tile(lng: float, lat: float, zoom: float):
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

    return tx, ty, zoom


def __transform_coords(feature: dict) -> None:
    for coords in feature["geometry"]["coordinates"]:
        for coord in coords:
            firstProjection = 'PROJCS["WGS 84 / Pseudo-Mercator",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Mercator_1SP"],PARAMETER["central_meridian",0],PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["X",EAST],AXIS["Y",NORTH],EXTENSION["PROJ4","+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs"],AUTHORITY["EPSG","3857"]]'
            secondProjection = Proj("epsg:4326")
            optimus_prime = Transformer.from_proj(firstProjection, secondProjection)
            coord[1], coord[0] = optimus_prime.transform(coord[0], coord[1])


def __locate_in_feature_collection(reference: int, layer: str, featureCollection: dict):
    """Devuelve un geojson con los datos geográficos de la parcela

    Args:
        parcela (int): Número de parcela
        featureCollection (dict): Objeto con los datos geográficos de la búsqueda

    Returns:
        Geojson: Objeto con los datos de la búsqueda
    """
    for feature in featureCollection["features"]:
        if feature["properties"][layer] == reference:
            __transform_coords(feature)
            return feature["geometry"]
    return None


def geometry_from_coords(layer: str, lat: float, lon: float, reference: int):
    """Devuelve un geojson con los datos geográficos de la búsqueda

    Args:
        layer (str): Capa de búsqueda [ municipios, poligonos, parcelas ]
        lat (float): Latitud
        lon (float): Longitud

    Returns:
        Geojson: Objeto con los datos de la búsqueda

    Raises:
        ValueError: Datos incorrectos
        KeyError: Capa no soportada
    """
    if not layer or not lat or not lon or not reference:
        raise ValueError("Datos incorrectos.")

    tile_x, tile_y, _ = __lng_lat_to_tile(lon, lat, 15)

    response = requests.get(
        f"{BASE_URL}/vectorsdg/vector/{layer}@3857/15.{tile_x}.{tile_y}.geojson"
    )

    print(f"{BASE_URL}/vectorsdg/vector/{layer}@3857/15.{tile_x}.{tile_y}.geojson")
    geojson_features = response.json()

    if layer in ["parcela", "recinto"]:
        return __locate_in_feature_collection(
            reference=reference, layer=layer, featureCollection=geojson_features
        )
    else:
        raise KeyError('Capa no soportada, solo se permite "parcela" y "recinto"')


def buscar(data: dict):
    """Devuelve un geojson con los datos geográficos de la búsqueda

    Args:
        data (dict): Objeto con los datos para el filtro [ comunidad, provincia, municipio, poligono, parcela ]

    Returns:
        Geojson: Objeto con los datos de la búsqueda
    """
    comunidad = data.get("comunidad", None)
    provincia = data.get("provincia", None)
    municipio = data.get("municipio", None)
    poligono = data.get("poligono", None)
    parcela = data.get("parcela", None)

    if not comunidad:
        if not provincia:
            raise ValueError(
                'No se ha especificado "comunidad" y no se puede obtener sin "provincia"'
            )
        else:
            comunidad = __findComunidad(provincia)

    if comunidad:
        if provincia:
            if municipio:
                if poligono:
                    if parcela:
                        response = requests.get(
                            f"{BASE_URL}/fega/ServiciosVisorSigpac/query/recintos/{provincia}/{municipio}/0/0/{poligono}/{parcela}.geojson"
                        )
                        geojson = response.json()
                        return geojson
                    else:
                        response = requests.get(
                            f"{BASE_URL}/fega/ServiciosVisorSigpac/query/parcelas/{provincia}/{municipio}/0/0/{poligono}.geojson"
                        )
                        geojson = response.json()
                        return geojson
                else:
                    response = requests.get(
                        f"{BASE_URL}/fega/ServiciosVisorSigpac/query/poligonos/{provincia}/{municipio}/0/0.geojson"
                    )
                    geojson = response.json()
                    return geojson
            else:
                response = requests.get(
                    f"{BASE_URL}/fega/ServiciosVisorSigpac/query/municipios/{provincia}.geojson"
                )
                geojson = response.json()
                return geojson
        else:
            response = requests.get(
                f"{BASE_URL}/fega/ServiciosVisorSigpac/query/provincias/{comunidad}.geojson"
            )
            geojson = response.json()
            return geojson

    else:
        raise ValueError('Se esperaba parametro "comunidad"')


if __name__ == "__main__":
    data = {
        "comunidad": 1,
        "provincia": 29,
        "municipio": 8,
        "poligono": 8,
        "parcela": 572,
    }
    geojson = buscar(data)
    print(geojson)
    x = geojson["features"][0]["properties"]["x1"]
    y = geojson["features"][0]["properties"]["y1"]
    print(x, y)

    print(geometry_from_coords("parcela", y, x, 572))

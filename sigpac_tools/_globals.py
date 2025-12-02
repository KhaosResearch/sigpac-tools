# URL from SIGPAC service
BASE_URL = "https://sigpac-hubcloud.es"
QUERY_URL = "servicioconsultassigpac/query"

# Provinces divided into communities
# https://www.ine.es/daco/daco42/codmun/cod_ccaa_provincia.htm
PROVINCES_BY_COMMUNITY = {
    1: [
        4,
        11,
        14,
        18,
        21,
        23,
        29,
        41,
    ],  # Andalucía : [Almería, Cádiz, Córdoba, Granada, Huelva, Jaén, Málaga, Sevilla]
    2: [22, 44, 50],  # Aragón : [Huesca, Teruel, Zaragoza]
    3: [33],  # Principado de Asturias : [Asturias]
    4: [7],  # Illes Balears : [Illes Balears]
    5: [35, 38],  # Canarias : [Las Palmas, Santa Cruz de Tenerife]
    6: [39],  # Cantabria : [Cantabria]
    7: [
        5,
        9,
        24,
        34,
        37,
        40,
        42,
        47,
        49,
    ],  # Castilla y León : [Ávila, Burgos, León, Palencia, Salamanca, Segovia, Soria, Valladolid, Zamora]
    8: [
        2,
        13,
        16,
        19,
        45,
    ],  # Castilla-La Mancha : [Albacete, Ciudad Real, Cuenca, Guadalajara, Toledo]
    9: [8, 17, 25, 43],  # Cataluña : [Barcelona, Girona, Lleida, Tarragona]
    10: [3, 12, 46],  # Comunitat Valenciana : [Alicante, Castellón, Valencia]
    11: [6, 10],  # Extremadura : [Badajoz, Cáceres]
    12: [15, 27, 32, 36],  # Galicia : [A Coruña, Lugo, Ourense, Pontevedra]
    13: [28],  # Comunidad de Madrid : [Madrid]
    14: [30],  # Región de Murcia : [Murcia]
    15: [31],  # Comunidad Foral de Navarra : [Navarra]
    16: [1, 20, 48],  # País Vasco : [Álava, Gipuzkoa, Bizkaia]
    17: [26],  # La Rioja : [La Rioja]
    18: [51],  # Ceuta : [Ceuta]
    19: [52],  # Melilla : [Melilla]
}

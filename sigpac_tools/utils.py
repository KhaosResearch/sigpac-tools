import structlog

from sigpac_tools._globals import PROVINCES_BY_COMMUNITY

logger = structlog.get_logger()

def find_community(province_id: int) -> int:
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


def read_cadastral_registry(registry: str) -> dict:
    """Read the cadastral reference, validates it and return its data as a dictionary.
    The expected format is:
        - 2 characters for the province
        - 3 characters for the municipality
        - 1 character for the section
        - 3 characters for the polygon
        - 5 characters for the parcel
        - 4 characters for the id
        - 2 characters for the control

    20 characters in total.

    Parameters
    ----------
        registry (str): Cadastrial reference to read

    Returns
    -------
        dict: Data extracted from the cadastral reference

    Raises
    -------
        ValueError: If the length of the cadastral reference is not 20 characters
    """
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

    # Will raise an error if the reference is not valid or if it is urban, in any other case, it will log the result and continue
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


def build_cadastral_reference(province: str, municipality: str, polygon: str, parcel_id: str):
    """
    Generates a valid RURAL cadastral reference with calculated control characters.

    Parameters
    ----------
    province (str):
        Province data. ID-NAME format.
    municipality (str):
        Municipality data. ID-NAME format.
    polygon (str):
        Polygon ID. Max: 3 digits.
    parcel_id (str):
        Parcel ID. Max: 5 digits.

    Returns
    -------
    cadastral_reference (str):
        Synthetic valid RURAL cadastral reference.
    """

    # --- 1. Prepare base components ---
    # Province (2 chars)
    prov = province.split('-')[0].zfill(2)

    # Municipality (3 chars)
    muni = municipality.split('-')[0].zfill(3)

    # Section (1 char) -> Use non-digit (e.g., "A") to ensure RURAL
    section = "A"

    # Polygon (3 chars)
    poly = str(polygon).zfill(3)

    # Parcel (5 chars)
    parcel = str(parcel_id).zfill(5)

    # ID (4 chars) -> usually zero unless you have sub-parcel identifiers
    parcel_id_4 = "".zfill(4)

    # --- 2. Combine without control characters ---
    partial_ref = prov + muni + section + poly + parcel + parcel_id_4  # 18 chars

    # --- 3. Calculate control characters (positions 19-20) ---
    code = get_control_characters(partial_ref)

    # --- 4. Final cadastral reference ---
    cadastral_reference = partial_ref + code

    logger.debug(f"FINAL CADASTRAL REF: {cadastral_reference}")
    return cadastral_reference


def get_control_characters(partial_ref: str) -> str:
    """
    Calculate the control characters for a given partial cadastral reference (without control characters)
    """
    res = "MQWERTYUIOPASDFGHJKLBZX"
    pos = [13, 15, 12, 5, 4, 17, 9, 21, 3, 7, 1]

    separated_ref = list(partial_ref)

    sum_pd1 = 0
    sum_sd2 = 0
    mixt1 = 0

    # First 7 characters
    for i in range(7):
        ch = separated_ref[i]
        if ch.isdigit():
            sum_pd1 += pos[i] * (ord(ch) - 48)
        else:
            sum_pd1 += pos[i] * ((ord(ch) - 63) if ord(ch)
                                 > 78 else (ord(ch) - 64))

    # Next 7 characters
    for i in range(7):
        ch = separated_ref[i + 7]
        if ch.isdigit():
            sum_sd2 += pos[i] * (ord(ch) - 48)
        else:
            sum_sd2 += pos[i] * ((ord(ch) - 63) if ord(ch)
                                 > 78 else (ord(ch) - 64))

    # Mixt calculation (last 4 digits before control)
    for i in range(4):
        mixt1 += pos[i + 7] * (ord(separated_ref[i + 14]) - 48)

    code1 = res[(sum_pd1 + mixt1) % 23]
    code2 = res[(sum_sd2 + mixt1) % 23]

    return code1 + code2


def validate_cadastral_registry(reference: str) -> None:
    """Validate the cadastral reference

    Given a cadastral reference, it validates if the reference is correct or not by comparing the present control characters with the calculated expected ones.

    Based on the code proposed by Emil in the comments of http://el-divagante.blogspot.com/2006/11/algoritmos-y-dgitos-de-control.html

    Parameters
    ----------
        reference (str): Cadastral reference to validate

    Returns
    -------
        None

    Raises
    -------
        ValueError: If the reference is not valid
        NotImplementedError: If the reference is urban
    """

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
                "Urban cadastral references are not supported yet. Please check the reference and try again."
            )

        if code1 == separated_ref[18] and code2 == separated_ref[19]:
            logger.info(f"Reference {reference} ({typo}) is valid.")
        else:
            raise ValueError(
                f"Reference {reference} ({typo}) is not valid. Expected control characters: {code1}{code2}, but got {separated_ref[18]}{separated_ref[19]}. Please check the reference and try again."
            )


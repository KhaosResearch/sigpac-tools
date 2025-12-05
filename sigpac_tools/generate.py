import structlog

logger = structlog.get_logger()

def build_cadastral_reference(province: str, municipality: str, polygon: str, parcel: str, enclosure: str=0, section: str = "A"):
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
    parcel (str):
        Parcel ID. Max: 5 digits.
    section (str)
        Section character. Max 1 char (A-Z. Default is A
    enclosure (str)
        Enclosure ID. Max 4 digits

    Returns
    -------
    cadastral_reference (str):
        Synthetic valid RURAL cadastral reference.
    """

    # --- 1. Prepare base components ---
    prov = province.split('-')[0].zfill(2)
    muni = municipality.split('-')[0].zfill(3)
    poly = str(polygon).zfill(3)
    parcel_id = str(parcel).zfill(5)
    enclosure_id = str(enclosure).zfill(4)

    # --- 2. Combine without control characters ---
    partial_ref = prov + muni + section + poly + parcel_id + enclosure_id  # 18 chars

    # --- 3. Calculate control characters (positions 19-20) ---
    code = calculate_control_characters(partial_ref)

    # --- 4. Final cadastral reference ---
    cadastral_reference = partial_ref + code

    # --- Check if its valid RURAL reference ---
    separated_ref = list(cadastral_reference)
    property_type = "URBAN" if separated_ref[5].isdigit() else "RURAL"

    if property_type == "URBAN":
        raise NotImplementedError(
            "Urban cadastral references are not supported yet. Please check the reference and try again."
        )

    logger.debug(f"Cadastral reference generated: {cadastral_reference}")
    return cadastral_reference


def calculate_control_characters(partial_ref: str) -> str:
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
        raise ValueError(
            "The cadastral reference must have a length of 20 characters")
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

if __name__ == '__main__':
    prov = 14,
    muni = 48,
    poly = 1,
    parcel = 199,

    syn_cadastral_ref = build_cadastral_reference(prov, muni, poly, parcel)
    logger.info(f"Synthetic cadastral reference generated: {syn_cadastral_ref}")

import pytest
from sigpac_tools.find import find_from_cadastral_registry


class TestFindCadastralRegistrySuite:
    @pytest.mark.parametrize(
        "cadastral_reg",
        [
            "06001A028000380000LH",
            "02086A005000020000LQ",
            "30024A284003000000IG",
            "29011A007000200000EQ",
            "38011A019001900000QY",
            "12079A012004430000HH",
            "47148A003000100000IH",
            "28043A062000010000AW",
            "12050A003001060000HA",
            "21035A023001690000QT",
            "06001a028000380000lh",
            "06 001 A 028 00038 0000 LH",
            "           06 001 a 028 000 38 0000 lh",
        ],
    )
    def test_cadastral_registry(self, cadastral_reg):
        result_geom, result_meta = find_from_cadastral_registry(cadastral_reg)
        assert result_geom is not None and result_meta is not None

    @pytest.mark.parametrize(
        "non_cadastral_reg",
        [
            "000000000000000000",
            "1" "AAAAAAAAAAAAAAAAAAAAAAAAAA" "5836065QB0353N0001IJ",
            "38011A019001900000XX",
            "????????????????????",
            "01000z000000000000MM",
        ],
    )
    def test_value_error_cadastral_registry(self, non_cadastral_reg):
        with pytest.raises(ValueError):
            find_from_cadastral_registry(non_cadastral_reg)

    @pytest.mark.parametrize(
        "non_cadastral_reg",
        [
            "9876113PB7197N0001OQ",
            "010001000000000000MM",
            "2755914VK4725F0001UT",
            "0709205UF7600N0001BL",
        ],
    )
    def test_not_implemented_error_cadastral_registry(self, non_cadastral_reg):
        with pytest.raises(NotImplementedError):
            find_from_cadastral_registry(non_cadastral_reg)


if __name__ == "__main__":
    pytest.main()

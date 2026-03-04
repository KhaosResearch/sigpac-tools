import pytest
from sigpac_tools.anotate import get_geometry_and_metadata_cadastral


class TestGetMetadata:
    def test_missing_layer(self):
        data = {
            "province": 1,
            "municipality": 1,
            "polygon": 1,
            "parcel": 1,
        }

        with pytest.raises(ValueError, match="Layer not specified"):
            get_geometry_and_metadata_cadastral("", data)

    def test_invalid_layer(self):
        data = {
            "province": 1,
            "municipality": 1,
            "polygon": 1,
            "parcel": 1,
        }

        with pytest.raises(KeyError):
            get_geometry_and_metadata_cadastral("invalid_layer", data)

    def test_missing_province(self):
        data = {
            "municipality": 1,
            "polygon": 1,
            "parcel": 1,
        }

        with pytest.raises(ValueError):
            get_geometry_and_metadata_cadastral("parcela", data)

    def test_missing_municipality(self):
        data = {
            "province": 1,
            "polygon": 1,
            "parcel": 1,
        }

        with pytest.raises(ValueError):
            get_geometry_and_metadata_cadastral("parcela", data)

    def test_missing_polygon(self):
        data = {
            "province": 1,
            "municipality": 1,
            "parcel": 1,
        }

        with pytest.raises(ValueError):
            get_geometry_and_metadata_cadastral("parcela", data)

    def test_missing_parcel(self):
        data = {
            "province": 1,
            "municipality": 1,
            "polygon": 1,
        }

        with pytest.raises(ValueError):
            get_geometry_and_metadata_cadastral("parcela", data)

    def test_missing_enclosure_recinto_layer(self):
        data = {
            "province": 1,
            "municipality": 1,
            "polygon": 1,
            "parcel": 1,
        }

        with pytest.raises(ValueError):
            get_geometry_and_metadata_cadastral("recinto", data)


if __name__ == "__main__":
    pytest.main()

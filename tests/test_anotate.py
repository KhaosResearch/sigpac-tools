import pytest
from unittest.mock import patch
from sigpac_tools.anotate import get_metadata

# Mock data for the test
layer_parcela_response = {"key": "value"}
layer_recinto_response = {"key": "value2"}


class TestGetMetadata:
    @patch("sigpac_tools.anotate.__query")
    def test_parcela_layer(self, mock_query):
        mock_query.return_value = layer_parcela_response
        data = {
            "province": 1,
            "municipality": 1,
            "polygon": 1,
            "parcel": 1,
        }

        result = get_metadata("parcela", data)
        assert result == layer_parcela_response

    @patch("sigpac_tools.anotate.__query")
    def test_recinto_layer(self, mock_query):
        mock_query.return_value = layer_recinto_response
        data = {
            "province": 1,
            "municipality": 1,
            "polygon": 1,
            "parcel": 1,
            "enclosure": 1,
        }

        result = get_metadata("recinto", data)
        assert result == layer_recinto_response

    def test_missing_layer(self):
        data = {
            "province": 1,
            "municipality": 1,
            "polygon": 1,
            "parcel": 1,
        }

        with pytest.raises(ValueError, match="Layer not specified"):
            get_metadata("", data)

    def test_invalid_layer(self):
        data = {
            "province": 1,
            "municipality": 1,
            "polygon": 1,
            "parcel": 1,
        }

        with pytest.raises(KeyError):
            get_metadata("invalid_layer", data)

    def test_missing_province(self):
        data = {
            "municipality": 1,
            "polygon": 1,
            "parcel": 1,
        }

        with pytest.raises(ValueError):
            get_metadata("parcela", data)

    def test_missing_municipality(self):
        data = {
            "province": 1,
            "polygon": 1,
            "parcel": 1,
        }

        with pytest.raises(ValueError):
            get_metadata("parcela", data)

    def test_missing_polygon(self):
        data = {
            "province": 1,
            "municipality": 1,
            "parcel": 1,
        }

        with pytest.raises(ValueError):
            get_metadata("parcela", data)

    def test_missing_parcel(self):
        data = {
            "province": 1,
            "municipality": 1,
            "polygon": 1,
        }

        with pytest.raises(ValueError):
            get_metadata("parcela", data)

    def test_missing_enclosure_recinto_layer(self):
        data = {
            "province": 1,
            "municipality": 1,
            "polygon": 1,
            "parcel": 1,
        }

        with pytest.raises(ValueError):
            get_metadata("recinto", data)


if __name__ == "__main__":
    pytest.main()

import pytest
from unittest.mock import patch, Mock
from sigpac_tools.search import search
from sigpac_tools._globals import BASE_URL

# Mock data for responses
provinces_response = {"type": "FeatureCollection", "features": []}
municipalities_response = {"type": "FeatureCollection", "features": []}
polygons_response = {"type": "FeatureCollection", "features": []}
parcels_response = {"type": "FeatureCollection", "features": []}
parcel_response = {"type": "FeatureCollection", "features": [{"id": "parcel"}]}


class TestSearch:
    @patch("sigpac_tools.search.requests.get")
    def test_search_provinces(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = provinces_response
        mock_get.return_value = mock_response

        data = {"community": 1}
        search(data)

        mock_get.assert_called_once_with(
            f"{BASE_URL}/fega/serviciosvisorsigpac/query/provincias/1"
        )

    @patch("sigpac_tools.search.requests.get")
    def test_search_municipalities(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = municipalities_response
        mock_get.return_value = mock_response

        data = {"province": 1}
        search(data)

        mock_get.assert_called_once_with(
            f"{BASE_URL}/fega/serviciosvisorsigpac/query/municipios/1"
        )

    @patch("sigpac_tools.search.requests.get")
    def test_search_polygons(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = polygons_response
        mock_get.return_value = mock_response

        data = {"province": 1, "municipality": 1}
        search(data)

        mock_get.assert_called_once_with(
            f"{BASE_URL}/fega/serviciosvisorsigpac/query/poligonos/1/1/0/0"
        )

    @patch("sigpac_tools.search.requests.get")
    def test_search_parcels(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = parcels_response
        mock_get.return_value = mock_response

        data = {"province": 1, "municipality": 1, "polygon": 1}
        search(data)

        mock_get.assert_called_once_with(
            f"{BASE_URL}/fega/serviciosvisorsigpac/query/parcelas/1/1/0/0/1"
        )

    @patch("sigpac_tools.search.requests.get")
    def test_search_specific_parcel(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = parcel_response
        mock_get.return_value = mock_response

        data = {"province": 1, "municipality": 1, "polygon": 1, "parcel": 1}
        search(data)

        mock_get.assert_called_once_with(
            f"{BASE_URL}/fega/serviciosvisorsigpac/query/recintos/1/1/0/0/1/1"
        )

    def test_missing_community_and_province(self):
        data = {"municipality": 1}
        with pytest.raises(
            ValueError,
            match='"Community" has not been specified, neither has been "province" and it is compulsory to find the community associated',
        ):
            search(data)

    def test_missing_community_not_found(self):
        data = {"parcel": 1}
        with pytest.raises(
            ValueError,
            match='"Community" has not been specified, neither has been "province" and it is compulsory to find the community associated',
        ):
            search(data)


if __name__ == "__main__":
    pytest.main()

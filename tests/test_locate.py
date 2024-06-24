import pytest
from unittest.mock import patch, Mock
from sigpac_tools.locate import geometry_from_coords
from sigpac_tools._globals import BASE_URL

# Mock data for the geojson response
mock_geojson_response = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "parcela": 123,
                "recinto": 456,
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[0, 0], [1, 1], [1, 0], [0, 0]]],
            },
        }
    ],
}

class TestGeometryFromCoords:
    @patch("sigpac_tools.locate.requests.get")
    @patch("sigpac_tools.locate.lng_lat_to_tile")
    @patch("sigpac_tools.locate.transform_coords")
    def test_geometry_from_coords_parcela(self, mock_transform_coords, mock_lng_lat_to_tile, mock_get):
        mock_lng_lat_to_tile.return_value = (1234, 5678)
        mock_response = Mock()
        mock_response.json.return_value = mock_geojson_response
        mock_get.return_value = mock_response

        layer = "parcela"
        lat = 40.0
        lon = -3.0
        reference = 123

        result = geometry_from_coords(layer, lat, lon, reference)

        mock_lng_lat_to_tile.assert_called_once_with(lon, lat, 15)
        mock_get.assert_called_once_with(f"{BASE_URL}/vectorsdg/vector/parcela@3857/15.1234.5678.geojson")
        mock_transform_coords.assert_called_once()
        assert result == mock_geojson_response["features"][0]["geometry"]

    @patch("sigpac_tools.locate.requests.get")
    @patch("sigpac_tools.locate.lng_lat_to_tile")
    @patch("sigpac_tools.locate.transform_coords")
    def test_geometry_from_coords_recinto(self, mock_transform_coords, mock_lng_lat_to_tile, mock_get):
        mock_lng_lat_to_tile.return_value = (1234, 5678)
        mock_response = Mock()
        mock_response.json.return_value = mock_geojson_response
        mock_get.return_value = mock_response

        layer = "recinto"
        lat = 40.0
        lon = -3.0
        reference = 456

        result = geometry_from_coords(layer, lat, lon, reference)

        mock_lng_lat_to_tile.assert_called_once_with(lon, lat, 15)
        mock_get.assert_called_once_with(f"{BASE_URL}/vectorsdg/vector/recinto@3857/15.1234.5678.geojson")
        mock_transform_coords.assert_called_once()
        assert result == mock_geojson_response["features"][0]["geometry"]

    @patch("sigpac_tools.locate.requests.get")
    @patch("sigpac_tools.locate.lng_lat_to_tile")
    def test_geometry_not_found(self, mock_lng_lat_to_tile, mock_get):
        mock_lng_lat_to_tile.return_value = (1234, 5678)
        mock_response = Mock()
        mock_response.json.return_value = {"type": "FeatureCollection", "features": []}
        mock_get.return_value = mock_response

        layer = "parcela"
        lat = 40.0
        lon = -3.0
        reference = 999

        result = geometry_from_coords(layer, lat, lon, reference)

        mock_lng_lat_to_tile.assert_called_once_with(lon, lat, 15)
        mock_get.assert_called_once_with(f"{BASE_URL}/vectorsdg/vector/parcela@3857/15.1234.5678.geojson")
        assert result is None

    def test_invalid_layer(self):
        with pytest.raises(KeyError, match='Layer "invalid" not supported. Supported layers: "parcela", "recinto"'):
            geometry_from_coords("invalid", 40.0, -3.0, 123)

    def test_missing_parameters(self):
        with pytest.raises(ValueError, match="Layer, latitude, longitude or reference not specified"):
            geometry_from_coords("", 40.0, -3.0, 123)
        with pytest.raises(ValueError, match="Layer, latitude, longitude or reference not specified"):
            geometry_from_coords("parcela", None, -3.0, 123)
        with pytest.raises(ValueError, match="Layer, latitude, longitude or reference not specified"):
            geometry_from_coords("parcela", 40.0, None, 123)
        with pytest.raises(ValueError, match="Layer, latitude, longitude or reference not specified"):
            geometry_from_coords("parcela", 40.0, -3.0, None)

if __name__ == "__main__":
    pytest.main()

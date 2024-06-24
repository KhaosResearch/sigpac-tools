import pytest

from sigpac_tools.utils import lng_lat_to_tile, transform_coords, findCommunity


class TestLngLatToTile:
    def test_central_coordinates(self):
        lng, lat, zoom = 0, 0, 1
        expected = (0, 0)
        assert lng_lat_to_tile(lng, lat, zoom) == expected

    def test_different_zoom_level(self):
        lng, lat, zoom = 0, 0, 2
        expected = (1, 1)
        assert lng_lat_to_tile(lng, lat, zoom) == expected

    def test_specific_coordinates(self):
        lng, lat, zoom = -3.7038, 40.4168, 10
        expected = (501, 637)
        assert lng_lat_to_tile(lng, lat, zoom) == expected


class TestTransformCoords:
    def test_transform_coordinates(self):
        feature = {
            "geometry": {
                "coordinates": [[[1492237.0, 6894685.0], [1492237.0, 6894685.0]]]
            }
        }

        transform_coords(feature)
        coords = feature["geometry"]["coordinates"][0][0]

        # Expected coordinates in EPSG:4326
        expected_coords = [13.3781405, 52.5150436]

        assert abs(round(coords[0], 6) - round(expected_coords[0], 6)) < 0.05
        assert abs(round(coords[1], 6) - round(expected_coords[1], 6)) < 0.05


class TestFindCommunity:
    def test_existing_province_id(self):
        province_id = 29
        expected = 1
        assert findCommunity(province_id) == expected

    def test_non_existing_province_id(self):
        province_id = 60
        assert findCommunity(province_id) is None

    def test_another_existing_province_id(self):
        province_id = 2
        expected = 8
        assert findCommunity(province_id) == expected


if __name__ == "__main__":
    pytest.main()

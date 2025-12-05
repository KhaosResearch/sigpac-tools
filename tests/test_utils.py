import pytest

from sigpac_tools.utils import (
    lng_lat_to_tile,
    transform_coords,
    find_community,
    read_cadastral_registry,
)


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
        assert find_community(province_id) == expected

    def test_non_existing_province_id(self):
        province_id = 60
        assert find_community(province_id) is None

    def test_another_existing_province_id(self):
        province_id = 2
        expected = 8
        assert find_community(province_id) == expected


class TestReadCadastralRegistry:
    def test_read_cadastral_registry_valid(self):
        registry = "29008A008005720000EQ"
        expected_result = {
            "province": 29,
            "municipality": 8,
            "section": "A",
            "polygon": 8,
            "parcel": 572,
            "id_inm": 0,
            "control": "EQ",
        }

        result = read_cadastral_registry(registry)
        assert result == expected_result

    def test_read_cadastral_registry_invalid_length(self):
        with pytest.raises(
            ValueError,
            match="The cadastral reference must have a length of 20 characters",
        ):
            read_cadastral_registry("29008A008005720000EQ000")
        with pytest.raises(
            ValueError,
            match="The cadastral reference must have a length of 20 characters",
        ):
            read_cadastral_registry("29008A00800572")

    def test_read_cadastral_registry_invalid_province(self):
        with pytest.raises(NotImplementedError):
            read_cadastral_registry("99003000100123456789")

if __name__ == "__main__":
    pytest.main()

import pytest
from sigpac_tools.locate import geometry_from_coords


class TestGeometryFromCoords:
    def test_invalid_layer(self):
        with pytest.raises(
            KeyError,
            match='Layer "invalid" not supported. Supported layers: "parcela", "recinto"',
        ):
            geometry_from_coords("invalid", 40.0, -3.0, 123)

    def test_missing_parameters(self):
        with pytest.raises(
            ValueError, match="Layer, latitude or longitude not specified"
        ):
            geometry_from_coords("", 40.0, -3.0, 123)
        with pytest.raises(
            ValueError, match="Layer, latitude or longitude not specified"
        ):
            geometry_from_coords("parcela", None, -3.0, 123)
        with pytest.raises(
            ValueError, match="Layer, latitude or longitude not specified"
        ):
            geometry_from_coords("parcela", 40.0, None, 123)


if __name__ == "__main__":
    pytest.main()

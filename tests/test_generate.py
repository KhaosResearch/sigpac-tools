import pytest

from sigpac_tools.generate import (
    build_cadastral_reference,
    calculate_control_characters,
    validate_cadastral_registry,
)
class TestBuildCadastralReference:
    def test_build_cadastral_reference_valid(self):
        prov = "26"
        muni = "002"
        poly = "001"
        parc = "00001"
        expected_result = "26002A001000010000EQ"

        result = build_cadastral_reference(prov, muni, poly, parc)
        assert result == expected_result

class TestCalculateControlCharacters:
    def test_calculate_control_characters_valid(self):
        partial_ref = "26002A001000010000"
        expected_result = "EQ"

        result = calculate_control_characters(partial_ref)
        assert result == expected_result

class TestValidateCadastralRegistry:
    def test_validate_cadastral_registry_valid(self):
        registry = "29008A008005720000EQ"
        validate_cadastral_registry(registry)  # This should pass without exceptions

    def test_validate_cadastral_registry_invalid_length(self):
        with pytest.raises(
            ValueError,
            match="The cadastral reference must have a length of 20 characters",
        ):
            validate_cadastral_registry("29008A008005720000EQ000")
        with pytest.raises(
            ValueError,
            match="The cadastral reference must have a length of 20 characters",
        ):
            validate_cadastral_registry("29008A00800572")

    def test_validate_cadastral_registry_urban_not_supported(self):
        registry = "9872023VH5797S0001WX"
        with pytest.raises(NotImplementedError):
            validate_cadastral_registry(registry)

    def test_validate_cadastral_registry_invalid_control(self):
        registry = "29008A008005720000OL"  # Incorrect control characters
        with pytest.raises(ValueError):
            validate_cadastral_registry(registry)

import pytest
from unittest.mock import patch, mock_open
import json
from old_main import (
    load_json_file,
    clean_js_content,
    parse_condition,
    evaluate_condition,
    query_vessels,
)


@pytest.fixture
def test_vessels():
    """Fixture providing test vessel data."""
    return [
        {
            "Z01_CURRENT_NAME": "Test Vessel 1",
            "P36_VESSEL_TYPE": "Tanker",
            "ZR1_BUILT": "2020-01",
            "Z13_STATUS_CODE": 4,
            "BUILDER_GROUP": "Test Builder",
            "A04_DWT_tonnes": 50000,
            "A05_GT": 30000,
        },
        {
            "Z01_CURRENT_NAME": "Test Vessel 2",
            "P36_VESSEL_TYPE": "Container",
            "ZR1_BUILT": "2019-01",
            "Z13_STATUS_CODE": 3,
            "BUILDER_GROUP": "Another Builder",
            "A04_DWT_tonnes": 45000,
            "A05_GT": 25000,
        },
    ]


class TestCleanJsContent:
    def test_with_js_variable(self):
        content = 'var vessels = [{"test": "data"}]'
        cleaned = clean_js_content(content)
        assert cleaned == '[{"test": "data"}]'

    def test_with_semicolon(self):
        content = '[{"test": "data"}];'
        cleaned = clean_js_content(content)
        assert cleaned == '[{"test": "data"}]'

    def test_with_both(self):
        content = 'var vessels = [{"test": "data"}];'
        cleaned = clean_js_content(content)
        assert cleaned == '[{"test": "data"}]'


class TestLoadJson:
    def test_load_json(self):
        mock_data = (
            '[{"Z01_CURRENT_NAME": "Test Vessel 1", "P36_VESSEL_TYPE": "Tanker"}]'
        )
        with patch("builtins.open", mock_open(read_data=mock_data)):
            result = load_json_file("test.json")
            assert len(result) == 1
            assert result[0]["Z01_CURRENT_NAME"] == "Test Vessel 1"

    def test_file_not_found(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                load_json_file("nonexistent.json")

    def test_invalid_json(self):
        mock_data = "invalid json"
        with patch("builtins.open", mock_open(read_data=mock_data)):
            with pytest.raises(json.JSONDecodeError):
                load_json_file("invalid.json")


class TestParseCondition:
    # Basic functionality tests using parameterization
    @pytest.mark.parametrize(
        "condition, expected",
        [
            # Standard numeric equality cases
            ("Z13_STATUS_CODE = 4", ("Z13_STATUS_CODE", "=", 4.0)),
            ("Z13_STATUS_CODE=4", ("Z13_STATUS_CODE", "=", 4.0)),
            ("Z13_STATUS_CODE  =  4", ("Z13_STATUS_CODE", "=", 4.0)),
            # Basic string equality cases
            (
                "BUILDER_GROUP = 'Guoyu Logistics'",
                ("BUILDER_GROUP", "=", "Guoyu Logistics"),
            ),
            (
                'BUILDER_GROUP = "Guoyu Logistics"',
                ("BUILDER_GROUP", "=", "Guoyu Logistics"),
            ),
        ],
        ids=[
            "numeric_equality_spaced",
            "numeric_equality_no_space",
            "numeric_equality_extra_space",
            "string_equality_single_quotes",
            "string_equality_double_quotes",
        ],
    )
    def test_basic_conditions(self, condition, expected):
        """Test basic condition parsing with various formats."""
        result = parse_condition(condition)
        assert result == expected

    # Different operators
    @pytest.mark.parametrize(
        "condition, expected_operator",
        [
            ("Z13_STATUS_CODE = 4", "="),
            ("Z13_STATUS_CODE != 4", "!="),
            ("Z13_STATUS_CODE < 4", "<"),
            ("Z13_STATUS_CODE > 4", ">"),
            ("Z13_STATUS_CODE <= 4", "<="),
            ("Z13_STATUS_CODE >= 4", ">="),
        ],
        ids=[
            "equal_operator",
            "not_equal_operator",
            "less_than_operator",
            "greater_than_operator",
            "less_equal_operator",
            "greater_equal_operator",
        ],
    )
    def test_operators(self, condition, expected_operator):
        """Test parsing different comparison operators."""
        _, operator, _ = parse_condition(condition)
        assert operator == expected_operator

    # Individual tests for important edge cases
    def test_parse_condition_with_period_in_string(self):
        """Test parsing a condition with a period in the string value, which was a known issue."""
        field, operator, value = parse_condition('BUILDER_GROUP = "Daehan S.B."')
        assert field == "BUILDER_GROUP"
        assert operator == "="
        assert value == "Daehan S.B."

    def test_parse_condition_with_spaces_in_string(self):
        """Test parsing a condition with multiple spaces in the string value."""
        field, operator, value = parse_condition(
            'DESCRIPTION = "This has    multiple   spaces"'
        )
        assert field == "DESCRIPTION"
        assert operator == "="
        assert value == "This has    multiple   spaces"

    def test_parse_condition_with_special_chars_in_string(self):
        """Test parsing a condition with special characters in the string value."""
        field, operator, value = parse_condition('NAME = "Vessel-123 (Special)"')
        assert field == "NAME"
        assert operator == "="
        assert value == "Vessel-123 (Special)"

    def test_parse_condition_with_numbers_in_field_name(self):
        """Test parsing a condition with numbers in the field name."""
        field, operator, value = parse_condition("Z13_STATUS_CODE = 4")
        assert field == "Z13_STATUS_CODE"
        assert operator == "="
        assert value == 4.0

    def test_parse_condition_float_value(self):
        """Test parsing a condition with a floating point value."""
        field, operator, value = parse_condition("LENGTH = 123.45")
        assert field == "LENGTH"
        assert operator == "="
        assert value == 123.45

    def test_parse_condition_negative_value(self):
        """Test parsing a condition with a negative number."""
        field, operator, value = parse_condition("TEMPERATURE = -15.5")
        assert field == "TEMPERATURE"
        assert operator == "="
        assert value == -15.5

    # Error cases
    def test_parse_condition_invalid_format(self):
        """Test that ValueError is raised for an invalid condition format."""
        with pytest.raises(ValueError) as excinfo:
            parse_condition("not a valid condition")
        assert "Invalid condition format" in str(excinfo.value)

    def test_parse_condition_missing_value(self):
        """Test handling a condition with a missing value."""
        with pytest.raises(ValueError):
            parse_condition("FIELD =")

    def test_parse_condition_missing_operator(self):
        """Test handling a condition with a missing operator."""
        with pytest.raises(ValueError):
            parse_condition("FIELD 123")

    def test_parse_condition_leading_trailing_whitespace(self):
        """Test parsing a condition with leading and trailing whitespace."""
        field, operator, value = parse_condition("  Z13_STATUS_CODE = 4  ")
        assert field == "Z13_STATUS_CODE"
        assert operator == "="
        assert value == 4.0


class TestEvaluateCondition:
    """Tests for evaluate_condition function."""

    def test_numeric_equality(self, test_vessels):
        record = test_vessels[0]
        assert evaluate_condition(record, "Z13_STATUS_CODE", "=", 4) is True
        assert evaluate_condition(record, "Z13_STATUS_CODE", "=", 3) is False

    def test_numeric_comparison(self, test_vessels):
        record = test_vessels[0]
        assert evaluate_condition(record, "Z13_STATUS_CODE", "<", 5) is True
        assert evaluate_condition(record, "Z13_STATUS_CODE", ">", 3) is True

    def test_string_equality(self, test_vessels):
        record = test_vessels[0]
        assert evaluate_condition(record, "BUILDER_GROUP", "=", "Test Builder") is True
        assert (
            evaluate_condition(record, "BUILDER_GROUP", "=", "Wrong Builder") is False
        )

    def test_nonexistent_field(self, test_vessels):
        record = test_vessels[0]
        assert evaluate_condition(record, "NON_EXISTENT", "=", "value") is False


class TestQueryVessels:
    """Tests for query_vessels function."""

    def test_single_condition(self, test_vessels):
        results = query_vessels(test_vessels, "WHERE Z13_STATUS_CODE = 4")
        assert len(results) == 1
        assert results[0]["Z01_CURRENT_NAME"] == "Test Vessel 1"

    def test_and_condition(self, test_vessels):
        results = query_vessels(
            test_vessels, "WHERE Z13_STATUS_CODE = 4 AND BUILDER_GROUP = 'Test Builder'"
        )
        assert len(results) == 1
        assert results[0]["Z01_CURRENT_NAME"] == "Test Vessel 1"

    def test_no_matches(self, test_vessels):
        results = query_vessels(test_vessels, "WHERE Z13_STATUS_CODE = 999")
        assert len(results) == 0

    def test_special_characters(self, test_vessels):
        test_vessels_with_special = test_vessels + [
            {"Z01_CURRENT_NAME": "Test Vessel 3", "BUILDER_GROUP": "Daehan S.B."}
        ]
        results = query_vessels(
            test_vessels_with_special, 'WHERE BUILDER_GROUP = "Daehan S.B."'
        )
        assert len(results) == 1
        assert results[0]["Z01_CURRENT_NAME"] == "Test Vessel 3"

    @pytest.mark.parametrize(
        "query,expected_count",
        [
            ("WHERE Z13_STATUS_CODE = 4", 1),
            ("WHERE Z13_STATUS_CODE = 3", 1),
            ("WHERE Z13_STATUS_CODE = 999", 0),
            ("WHERE P36_VESSEL_TYPE = 'Tanker'", 1),
            ("WHERE P36_VESSEL_TYPE = 'Container'", 1),
        ],
    )
    def test_multiple_queries(self, test_vessels, query, expected_count):
        results = query_vessels(test_vessels, query)
        assert len(results) == expected_count

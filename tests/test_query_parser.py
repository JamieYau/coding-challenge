import pytest
from inmemorydb.query_parser import QueryParser


# tests parsing complete queries
class TestParseQuery:
    @pytest.mark.parametrize(
        "query,expected",
        [
            ("WHERE field = 5", [("field", "=", 5.0)]),
            ("WHERE field = 'text'", [("field", "=", "text")]),
            ("WHERE a=1 AND b=2", [("a", "=", 1.0), ("b", "=", 2.0)]),
        ],
    )
    def test_parse_query(self, query, expected):
        assert QueryParser.parse_query(query) == expected

    def test_no_conditions(self):
        with pytest.raises(ValueError):
            QueryParser.parse_query("WHERE")


# tests parsing single conditions
class TestParseCondition:
    @pytest.mark.parametrize(
        "condition,expected",
        [
            ("field = 5", ("field", "=", 5.0)),
            ("field != 'text'", ("field", "!=", "text")),
            ("a < 1", ("a", "<", 1.0)),
        ],
    )
    def test_parse_condition(self, condition, expected):
        assert QueryParser.parse_condition(condition) == expected


class TestSplitConditions:
    @pytest.mark.parametrize(
        "conditions_str,expected",
        [
            ("field = 5 AND field2 = 10", ["field = 5", "field2 = 10"]),
            ("a=1 AND b=2 AND c=3", ["a=1", "b=2", "c=3"]),
            ("x > 0 AND y < 5", ["x > 0", "y < 5"]),
        ],
    )
    def test_split_conditions(self, conditions_str, expected):
        assert QueryParser._split_conditions(conditions_str) == expected


class TestEvaluateCondition:
    @pytest.mark.parametrize(
        "record,field,operator,value,expected",
        [
            ({"field": 5}, "field", "=", 5, True),
            ({"field": 5}, "field", "!=", 10, True),
            ({"field": 5}, "field", "<", 10, True),
            ({"field": 5}, "field", ">", 3, True),
            ({"field": 5}, "field", "<=", 5, True),
            ({"field": 5}, "field", ">=", 5, True),
            ({"field": 5}, "other_field", "=", 5, False),
        ],
    )
    def test_evaluate_condition(self, record, field, operator, value, expected):
        assert (
            QueryParser.evaluate_condition(record, field, operator, value) == expected
        )


class TestEvaluateRecord:
    @pytest.mark.parametrize(
        "record,conditions,expected",
        [
            ({"field": 5}, [("field", "=", 5)], True),
            ({"field": 5}, [("field", "!=", 10)], True),
            ({"field": 5}, [("field", "<", 10)], True),
            ({"field": 5}, [("field", ">", 3)], True),
            ({"field": 5}, [("field", "<=", 5)], True),
            ({"field": 5}, [("field", ">=", 5)], True),
            ({"field": 5}, [("other_field", "=", 5)], False),
        ],
    )
    def test_evaluate_record(self, record, conditions, expected):
        assert QueryParser.evaluate_record(record, conditions) == expected


class TestParseValue:
    @pytest.mark.parametrize(
        "value_str,expected",
        [
            ("5", 5.0),
            ("'text'", "text"),
            ("'123'", "123"),
            ("'12.34'", "12.34"),
            ("'true'", "true"),
            ("'false'", "false"),
        ],
    )
    def test_parse_value(self, value_str, expected):
        assert QueryParser._parse_value(value_str) == expected

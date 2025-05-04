import pytest
from inmemorydb.database import Database


class TestInit:
    def test_init_with_data(self, sample_vessels):
        db = Database(sample_vessels)
        assert db.count() == 2


class TestCleanJsContent:
    def test_clean_js_content(self):
        content = 'var vessels = [{"test": "data"}];'
        cleaned = Database._clean_js_content(content)
        assert cleaned == '[{"test": "data"}]'

    def test_clean_js_content_no_var(self):
        content = '[{"test": "data"}]'
        cleaned = Database._clean_js_content(content)
        assert cleaned == content


class TestFromJsonFile:
    def test_from_json_file(self, mock_json_file, sample_vessels):
        db = Database.from_json_file(mock_json_file)
        assert db.count() == len(sample_vessels)

    def test_invalid_json(self, tmp_path):
        invalid_json_path = tmp_path / "invalid.json"
        invalid_json_path.write_text("Invalid JSON content")
        with pytest.raises(ValueError):
            Database.from_json_file(invalid_json_path)

    def test_file_not_found(self, tmp_path):
        non_existent_file = tmp_path / "non_existent.json"
        with pytest.raises(FileNotFoundError):
            Database.from_json_file(non_existent_file)


class TestQuery:
    def test_query_empty(self, sample_vessels):
        db = Database(sample_vessels)
        with pytest.raises(ValueError):
            db.query("")

    def test_query_invalid(self, sample_vessels):
        db = Database(sample_vessels)
        with pytest.raises(ValueError):
            db.query("INVALID QUERY")

    @pytest.mark.parametrize(
        "query,expected_count",
        [
            ("WHERE Z13_STATUS_CODE = 4", 1),
        ],
    )
    def test_query_valid(self, query, expected_count, sample_vessels):
        db = Database(sample_vessels)

        results = db.query(query)
        assert len(results) == expected_count
        assert results[0]["Z01_CURRENT_NAME"] == "Vessel 1"

    # test query with multiple conditions

    # test query with invalid field name

    # test query with no results


class TestCount:
    def test_count(self, sample_vessels):
        db = Database(sample_vessels)
        assert db.count() == 2

    def test_count_empty(self):
        db = Database([])
        assert db.count() == 0

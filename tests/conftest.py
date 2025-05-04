import pytest
import json


# This file contains fixtures for testing inmemorydb module
# Fixtures are reusable components that can be used in multiple test cases.
@pytest.fixture
def sample_vessels():
    return [
        {
            "Z01_CURRENT_NAME": "Vessel 1",
            "Z13_STATUS_CODE": 4,
            "BUILDER_GROUP": "Guoyu Logistics",
        },
        {
            "Z01_CURRENT_NAME": "Vessel 2",
            "Z13_STATUS_CODE": 3,
            "BUILDER_GROUP": "Other Builder",
        },
    ]


@pytest.fixture
def mock_json_file(tmp_path, sample_vessels):
    """Create a temporary JSON file for testing."""
    file_path = tmp_path / "vessels.json"
    file_path.write_text(json.dumps(sample_vessels))
    return file_path

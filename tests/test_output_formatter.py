import pytest
import json
from inmemorydb.output_formatter import OutputFormatter, OutputFormat


class TestOutputFormatter:
    @pytest.fixture
    def sample_results(self):
        return [{"name": "Vessel 1"}, {"name": "Vessel 2"}]

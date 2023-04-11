from src.functions import get_settings

import os


def test_settings():
    assert os.environ.get('RUNNING_TESTS', False)
    assert "PostgresOptions" in get_settings().keys()

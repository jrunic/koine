import pytest
from tests.fixtures import seed


@pytest.fixture
def koine_home(tmp_path):
    return seed.montar(str(tmp_path))

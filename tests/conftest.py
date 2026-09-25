import pytest

from tests.juiz import obter_juiz


@pytest.fixture(scope="session")
def juiz():
    return obter_juiz()

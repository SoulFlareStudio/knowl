import pytest
from knowl import OntologyDatabase, DBConfig, OntologyAPI
from rdflib.namespace import FOAF, DOAP, OWL, DC


def test_basic_inmemory_setup():
    config = DBConfig(DBConfig.IN_MEMORY)
    ontoDB = OntologyDatabase(config)
    with pytest.raises(RuntimeError):
        ontoDB.setup()  # if does not exist
    ontoDB.setup(create=True)
    ontoDB.destroy("I know what I am doing")

# def inMemoryAPISetup(self):

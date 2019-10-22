import pytest
from knowl import OntologyDatabase, DBConfig, OntologyAPI
from rdflib.namespace import FOAF, DOAP, OWL, DC


@pytest.main.db_connection_tesing
def test_basic_inmemory_setup():
    config = DBConfig(DBConfig.IN_MEMORY)
    ontoDB = OntologyDatabase(config)
    with pytest.raises(RuntimeError):
        # this should raise error, since DB does not exist and "create" is False
        ontoDB.setup()
    ontoDB.setup(create=True)
    with pytest.raises(ValueError):
        # calling "DB.destroy" with an incorrect confirmation string should fail
        ontoDB.destroy("I have no idea what this does!")
    ontoDB.destroy("I know what I am doing")

# def inMemoryAPISetup(self):

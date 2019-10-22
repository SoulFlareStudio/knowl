import pytest
from knowl import OntologyDatabase, DBConfig, OntologyAPI
from rdflib.namespace import FOAF, DOAP, OWL, DC
from rdflib import Literal, URIRef


@pytest.mark.db_config_testing
def test_in_memory_config():
    config = DBConfig(DBConfig.IN_MEMORY, database="")
    assert config.DB_URI == "sqlite://", "The database URI for an in-memory DB is not correct!"
    assert config.getDB_URI() == Literal("sqlite://"), "The database URI for an in-memory DB is not correct!"


@pytest.mark.db_config_testing
def test_db_properties():
    dbName = "testing_ontology"
    dbIRI = "http://dbpedia.org/ontology/"
    nss = {"foaf": FOAF, "doap": DOAP, "dc": DC}
    config = DBConfig(database=dbName, baseURL=dbIRI, namespaces=nss)
    assert config.database == dbName, "Database name was not set correctly"
    assert config.baseURL == URIRef(dbIRI), "Base URL/URI/IRI for the ontology was not set correctly."
    for k, v in nss.items():
        assert k in config.namespaces and config.namespaces[k] == v, "Something went wrong while setting the namespaces"

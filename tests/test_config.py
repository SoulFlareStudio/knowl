import pytest
from knowl import OntologyDatabase, DBConfig, OntologyAPI
from rdflib.namespace import FOAF, DOAP, OWL, DC
from rdflib import Literal, URIRef


def test_in_memory_config():
    config = DBConfig(DBConfig.IN_MEMORY, database="")
    assert config.DB_URI == "sqlite://"  # "The database URI for an in-memory DB is not correct!"
    assert config.getDB_URI() == Literal("sqlite://")


def test_db_properties():
    dbName = "testing_ontology"
    dbIRI = "http://dbpedia.org/ontology/"
    nss = {"foaf": FOAF, "doap": DOAP, "dc": DC}
    config = DBConfig(database=dbName, baseURL=dbIRI, namespaces=nss)
    assert config.database == dbName
    assert config.baseURL == URIRef(dbIRI)
    for k, v in nss.items():
        assert k in config.namespaces and config.namespaces[k] == v

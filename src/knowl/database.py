# -*- coding: utf-8 -*-
"""
@author: Radoslav Škoviera

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

import rdflib
from rdflib import Graph, Namespace
from rdflib_sqlalchemy.store import SQLAlchemy

from knowl import DBConfig

from rdflib import URIRef, BNode, Literal
from rdflib.term import Identifier

from rdflib.namespace import FOAF, RDF, RDFS


def interact_with_db(func: callable):
    """This function is used as a wrapper for most DB interacting functions.
    Its purpose is to take care of the fact that the connection to the DB can
    occasionally fail after some period of inactivity.

    Parameters
    ----------
    func : callable
        A function to be called

    Returns
    -------
    [type]
        Returns the value returned by the callable function. Return type depends on the returned value.
    """
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            print("Query Error", e)
            print("Query arguments:")
            print(args, kwargs)
            self.closelink()
            self.setup()
            print("Re-connected", e)
            return func(self, *args, **kwargs)

    return wrapper


class OntologyDatabase:
    """A front-end of an ontology database. This class provides "safe" access to most of the standard
    operations provided by the rdflib.Graph class. The "safeness" of the methods lies in catching
    exceptions and reconnecting shall the connection to the database "die" for whatever reason.
    Additionally, this class implements the SQLAlchemy store for the triples

    """

    def __init__(self, config=None, create=None):
        """Create ontology database API with SQLAlchemy store.

        Parameters
        ----------
        config : [str, knowl.DBConfig], optional
            The path to a configuration file or the configuration object. By default None,
            which results in a configuration with default parameters (see knowl.DBConfig).
        create : bool, optional
            Whether or not the tables for the ontology (triplestore) should be initalized.
            Set to True if you are creating a new database, by default None.
            As per SQLAlchemy documentation, the creation operation is idempotent. Thus,
            could be left at True, unless you specifically do not want to create a new database
            if one does not exist.
        """
        # initialize database config
        self.__config = DBConfig.factory(config)

        self.__username = None
        self.__password = None
        self.__create = create

        # configure database identifier (ontology IRI/base URL)
        self.__identifier = self.config.baseURL

        self.__store = SQLAlchemy(identifier=self.identifier)
        self._graph = Graph(self.__store, identifier=self.identifier)

    def setup(self, create=False, username: str = None, password: str = None):
        """Sets-up a new database connection. Call this to initialize access to the database.

        Parameters
        ----------
        create : bool, optional
            Whether the tables should be created (idempotent). Only set to True if creating a new database, by default False.
            Setting the object property self.create to anything but None will override this value!
        username : str, optional
            Database access credentials. Only set this if you didn't set it before (e.g. in the config file), by default None
        password : str, optional
            Database access credentials. Only set this if you didn't set it before (e.g. in the config file), by default None
        """
        if self.__create is not None:
            create = self.__create
        self._graph.open(self.config.getDB_URI(self.__username if username is None else username, self.__password if password is None else password),
                         create=create)
        for ns, uri in self.config.namespaces.items():
            self._graph.bind(ns.lower(), uri)

    def closelink(self):
        """Closes the database connection.
        """
        try:
            self._graph.close()
        except Exception as e:
            print("Exception in Closing", e)

    def destroy(self, confirmation: str = None):
        """Destroys the store for the Ontology

        This will erase/destroy the database (triplestore) used to store the data.
        Be very careful when calling this function.

        Parameters
        ----------
        confirmation : str, optional
            [description], by default None
        """
        if confirmation == "I know what I am doing":
            self._graph.destroy(self.identifier)

    def setCredentials(self, username: str = None, password: str = None):
        """Set access credentials for the database server containing the triplestore.

        Parameters
        ----------
        username : str, optional
            The username, by default None
        password : str, optional
            The password. Warning, this will be visible in the DB URL! By default None
        """
        self.__username = username
        self.__password = password

    @interact_with_db
    def mergeFileIntoDB(self, filepath: str):
        """Merge an existing ontology file into the current database. This could be used to populate
        a new ontology from an existing one stored as a file. The ontology is automatically merged
        and stored in the triplestore database server after calling this function.

        Parameters
        ----------
        filepath : str
            Path to the file containing the ontology. See RDFLib documentation,
            specifically, the function Graph.parse for supported formats.
        """
        tmpGraph = Graph()
        tmpGraph.parse(filepath)
        self._graph += tmpGraph

    @property
    def config(self):
        return self.__config

    @property
    def identifier(self):
        return self.__identifier

    @interact_with_db
    def bind(self, prefix, namespace, override=True):
        self._graph.bind(prefix.lower(), namespace, override)

    @interact_with_db
    def query(self, *args, **kwargs):
        return self._graph.query(*args, **kwargs)

    @interact_with_db
    def add(self, triple: tuple):
        """Adds a triple (s, p, o) into the database.
        This function is only a "safe" re-implementation of the original rdflib graph function.
        See rdflib.Graph documentation for more information.

        Parameters
        ----------
        triple : tuple
            (s, p, o) triple
        """
        self._graph.add(triple)

    @interact_with_db
    def addN(self, triples: list):
        """Adds n-triples into the database. This method is faster than adding
        individual triples one-by-one using the "add" method. This function
        also automatically adds the current graph as the context (unlike
        the original method from rdflib).
        This function is only a "safe" re-implementation of the original rdflib graph function.
        See rdflib.Graph documentation for more information.

        Parameters
        ----------
        triples : list
            list of (s, p, o) triples to be added into the database
        """
        # automatically add self.graph as context if not specified directly
        quads = [t + (self._graph,) for t in triples if len(t) == 3]
        self._graph.addN(quads)

    @interact_with_db
    def remove(self, triple: tuple):
        """Remove the specified triple or triples from the database.
        Not all fields of the triple needs to be specified. Omitted parts
        shall be replaced with "None" value.
        In such case, all triples matching the provided variables
        are removed.
        E.g., (someEntity, None, None) will remove containing "someEntity"
        as subject.

        This function is only a "safe" re-implementation of the original rdflib graph function.
        See rdflib.Graph documentation for more information.

        Parameters
        ----------
        triple : tuple
            (s, p, o) triple
        """
        self._graph.remove(triple)

    @interact_with_db
    def triples(self, triple: tuple):
        """Returns a generator for triples matching the provided pattern.
        The pattern/template triple can contain concrete values or None
        where the item shall be matched to anything.
        E.g., (None, RDF.type, None) will return all triples containing
        RDF.type as the predicate.

        This function is only a "safe" re-implementation of the original rdflib graph function.
        See rdflib.Graph documentation for more information.

        Parameters
        ----------
        triple : tuple
            (s, p, o) triple

        Returns
        -------
        generator
            generator of matching triples
        """
        return self._graph.triples(triple)

    @interact_with_db
    def subjects(self, predicate: Identifier = None, object: Identifier = None):
        """Returns a (list of) subject(s) matching the values provided as predicate
        and object. Similarly to triples, wildcard items can be replaced with None.

        This function is only a "safe" re-implementation of the original rdflib graph function.
        See rdflib.Graph documentation for more information.

        Parameters
        ----------
        predicate : Identifier, optional
            p, by default None
        object : Identifier, optional
            o, by default None

        Returns
        -------
        generator
            Subjects matching the query
        """
        return self._graph.subjects(predicate, object)

    @interact_with_db
    def subject_objects(self, predicate: Identifier = None):
        """Returns subjects and objects matching the value provided as predicate.

        See "subjects" and "triples" methods for more info.

        This function is only a "safe" re-implementation of the original rdflib graph function.
        See rdflib.Graph documentation for more information.

        Parameters
        ----------
        predicate : Identifier, optional
            p, by default None

        Returns
        -------
        generator
            The subjects and objects matching where predicate is set to the provided value
        """
        return self._graph.subject_objects(predicate)

    @interact_with_db
    def subject_predicates(self, object: Identifier = None):
        """Returns subjects and predicates matching the value provided as object.

        See "subjects" and "triples" methods for more info.

        This function is only a "safe" re-implementation of the original rdflib graph function.
        See rdflib.Graph documentation for more information.

        Parameters
        ----------
        object : Identifier, optional
            o, by default None

        Returns
        -------
        generator
            The subjects and predicates matching the query
        """
        return self._graph.subject_predicates(object)

    @interact_with_db
    def objects(self, subject: Identifier = None, predicate: Identifier = None):
        """Returns (a list of) object(s) matching the query.

        See "subjects" and "triples" methods for more info.

        This function is only a "safe" re-implementation of the original rdflib graph function.
        See rdflib.Graph documentation for more information.

        Parameters
        ----------
        subject : Identifier, optional
            s, by default None
        predicate : Identifier, optional
            p, by default None

        Returns
        -------
        generator
            The objects matching the query
        """
        return self._graph.objects(subject, predicate)

    @interact_with_db
    def predicates(self, subject: Identifier = None, object: Identifier = None):
        """Returns (a list of) predicate(s) matching the query.

        See "subjects" and "triples" methods for more info.

        This function is only a "safe" re-implementation of the original rdflib graph function.
        See rdflib.Graph documentation for more information.

        Parameters
        ----------
        subject : Identifier, optional
            s, by default None
        object : Identifier, optional
            o, by default None

        Returns
        -------
        generator
            The predicates matching the query.
        """
        return self._graph.predicates(subject, object)

    @interact_with_db
    def predicate_objects(self, subject: Identifier = None):
        """Returns predicates and objects where the subject matches
        the value specified in the function parameter.

        See "subjects" and "triples" methods for more info.

        This function is only a "safe" re-implementation of the original rdflib graph function.
        See rdflib.Graph documentation for more information.

        Parameters
        ----------
        subject : Identifier, optional
            s, by default None

        Returns
        -------
        generator
            The predicates and objects matching the query
        """
        return self._graph.predicate_objects(subject)

    @interact_with_db
    def transitive_subjects(self, predicate: Identifier, object: Identifier):
        """This function transitively generates subjects for the object,
        using only the value specified as predicate as the property.
        I.e., it "walks backwards" using only the predicate.
        E.g., transitive_subjects(parentOf, entity) will generate
        all ancestor of the object "entity".

        See "subjects" and "triples" methods for more info.

        This function is only a "safe" re-implementation of the original rdflib graph function.
        See rdflib.Graph documentation for more information.

        Parameters
        ----------
        predicate : Identifier
            p
        object : Identifier
            o

        Returns
        -------
        generator
            Generator of subjects matching the query.
        """
        return self._graph.transitive_subjects(predicate, object)

    @interact_with_db
    def transitive_objects(self, subject: Identifier, property: Identifier):
        """This function generates objects for the subject using only the property.
        It is the revers of "transitive_subjects". I.e., it "walks forwards"
        in the ontology, using only the property/predicate.
        E.g., transitive_objects(entity, hasComponent) will generate all objects
        that are part of the entity (i.e., all the components of the entity).

        See "subjects" and "triples" methods for more info.

        This function is only a "safe" re-implementation of the original rdflib graph function.
        See rdflib.Graph documentation for more information.

        Parameters
        ----------
        subject : Identifier
            s
        property : Identifier
            p

        Returns
        -------
        generator
            Objects matchting the query
        """
        return self._graph.transitive_objects(subject, property)

    @interact_with_db
    def set(self, triple: set):
        """Convenience function for "set" operations in the database.
        Values set by this function are first removed and than assigned,
        ensuring there is only one record for the specified subject + property.

        This function is only a "safe" re-implementation of the original rdflib graph function.
        See rdflib.Graph documentation for more information.

        Parameters
        ----------
        triple : set
            (s, p, o) triple
        """
        self._graph.set(triple)

    @interact_with_db
    def value(self, subject: Identifier = None, predicate: Identifier = RDF.value, object: Identifier = None, default=None, any=True):
        """Complementery function for the "set" method. It expects that there is only one value
        matching the subject + predicate combination. Error is risen otherwise!

        This function is only a "safe" re-implementation of the original rdflib graph function.
        See rdflib.Graph documentation for more information.

        Parameters
        ----------
        subject : Identifier, optional
            s, by default None
        predicate : Identifier, optional
            p, by default RDF.value
        object : Identifier, optional
            o, by default None
        default : any, optional
            Default value to be returned if it is not specified in the database, by default None
        any : bool, optional
            No idea, see rdflib documentation, by default True

        Returns
        -------
        any
            The expected value
        """
        return self._graph.value(subject, predicate, object, default, any)

    @interact_with_db
    def compute_qname(self, uri):
        return self._graph.compute_qname(uri)

    @interact_with_db
    def __getitem__(self, item):
        """Convenience function. Allows queries/triples to be specified via the "object[index]"
        notation.

        This function is only a "safe" re-implementation of the original rdflib graph function.
        See rdflib.Graph documentation for more information.
        """
        return self._graph.__getitem__(item)

    @interact_with_db
    def __len__(self):
        """Allows the use of the len(container) function to return the number of entries in the database

        This function is only a "safe" re-implementation of the original rdflib graph function.
        See rdflib.Graph documentation for more information.
        """
        return len(self._graph)

    @interact_with_db
    def __contains__(self, item):
        """Allows the use of "item in container" notation to be used to test if database contains entries
        matching the query. The item shall be an (s, p, o) triple, obeying the standard contrains.

        This function is only a "safe" re-implementation of the original rdflib graph function.
        See rdflib.Graph documentation for more information.
        """
        return item in self._graph

    @property
    def graph(self):
        # REMOVE: temporal debugging property, shall not be present at release
        return self._graph

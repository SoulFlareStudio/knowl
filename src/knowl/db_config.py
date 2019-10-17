# -*- coding: utf-8 -*-
"""
@author: Radoslav Škoviera

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from rdflib.namespace import FOAF
from rdflib import Literal, URIRef
from warnings import warn
import os
import yaml
import json


class MissingParameterWarning(Warning):
    """Helper class meaning a necessary parameter was not provided.
    """
    pass


class DBConfig(object):

    @staticmethod
    def getInMemoryConfig(database: str = "onto",
                          baseURL: str = "http://dbpedia.org/ontology/",
                          namespaces: dict = {"foaf": FOAF}):
        return DBConfig(host=DBConfig.IN_MEMORY, database=database, baseURL=baseURL, namespaces=namespaces)

    @staticmethod
    def factory(cfg=None):
        """Universal factory funciton for creating a database config.
        One of three parameters could be specified:
            None - will create a new config with the default parameters
            str - path to the YAML or JSON file containing the configuration parameters
            DBConfig - an already initialized configuration object
        The purpose of this factory funciton is to make universal interface.

        Parameters
        ----------
        cfg : [None, str, DBConfig], optional
            Initialization parameters for the configuration object, by default None

        Returns
        -------
        DBConfig
        """
        if cfg is None:
            config = DBConfig()
        elif isinstance(cfg, str):
            config = DBConfig.fromFile(cfg)
        else:
            config = cfg
        return config

    @staticmethod
    def fromFile(filepath: str):
        """Initialize the config from a YAML or JSON file. The configuration could be partial,
        i.e. the values not directly specified in the file will be initialized
        with the default values (see DBConfig constructor)

        Parameters
        ----------
        filepath : str
            Path to the configuration file

        Returns
        -------
        DBConfig
            The configuration object with values inilitalized from the provided
        """
        _, extension = os.path.splitext(filepath)
        extension = extension[1:].lower()
        with open(filepath, 'r') as file:
            if any([ext in extension.lower() for ext in ['yaml', 'yml']]):
                cfg = yaml.safe_load(file)
            elif 'json' in extension.lower():
                cfg = json.load(file)
        return DBConfig(**cfg)

    IN_MEMORY = "sqlite://"

    def __init__(self, host: str = "127.0.0.1", port: int = 3306,
                 username: str = None, password: str = None,
                 dialect: str = "mysql", driver: str = "pymysql",
                 database: str = "onto",
                 baseURL: str = "http://dbpedia.org/ontology/",
                 namespaces: dict = {"foaf": FOAF}):
        """Creates a configuration object for RDFLib-SQLAlchemy store database.

        Parameters
        ----------
        host : str, optional
            The location/hostname (e.g. IP address) where the database is running.
            Use the "localhost" to target DB running on the local machine -which is also the default "127.0.0.1"
        port : int, optional
            The port on which the database server is running, by default 3306
        username : str, optional
            Username credential to sign into the database. Make sure the provided user
            has the proper rights for the database, by default the username is not specified
        password : str, optional
            The password for the user. Warning: this is visible in the DB URI string!, by default the password is not specified
        dialect : str, optional
            Database "dialect", e.g., mysql, postgresql and so on. Search for SQLAlchemy dialects for more info, by default "mysql"
        driver : str, optional
            Driver for the database, i.e. the library that will be used to communicate with the database.
            Make sure to install and select the proper driver for the chosen dialect, by default "pymysql"
        database : str, optional
            Name of the specific database on the database server, where data will be saved, by default "onto"
        baseURL : str, optional
            Base URL or ontology IRI. This is basically the identifier of the ontology.
            Multiple ontologies can coexist inside a single database (specified by the "database" argument)
            provided they have different identifiers. Also, objects from an ontology with different IRI/base URL
            are not visible to other ontology IRI, by default "http://dbpedia.org/ontology/"
        namespaces : dict, optional
            Additional namespaces to bind to the database. When creating custom ontology classes,
            you are most likely using a custom namespace (e.g. your ontology IRI). You can bind that namespace
            (add shorthand reference to it) by specifing it here. Also, additional/non-standard namespaces
            or collections of ontology classes can be provided, by default {"foaf": FOAF}
        """

        self.__host = host
        self.__port = port
        self.__username = username
        self.__password = password
        self.__dialect = dialect
        self.__driver = driver
        self.__database = database
        self.__baseURL = URIRef(baseURL)
        self.__namespaces = namespaces

        self.__namespaces["base"] = self.baseURL + "#"

        if host == self.IN_MEMORY:
            self.__DB_URI = self.IN_MEMORY
            self.__dialect = "sqlite"
            self.__driver = "sqlite"
        else:
            self.__DB_URI = "{dialect}+{driver}://{username}:{password}@{host}:{port}/{database}"

    @property
    def uniqueID(self):
        """Complete unique identifier of the specific ontology. Unlike the IRI or the DB URI,
        this ID takes into consideration both resource identifiers and combines them. Also,
        unlike the DB URI, which includes the plain login credentials for the database,
        this ID is hashed, therefore it can be used as a public identifier without
        the risk of exposing sensitive information.
        The property only works properly if access credentials are set. Otherwise,
        it is recommended to use the "getUniqueID function that allows to enter the credentials.

        Returns
        -------
        int
            Hashed ID of the specific ontology database.
        """
        return hash(self.getDB_URI() + self.baseURL)

    def getUniqueID(self, username: str = None, password: str = None):
        """Works exactly like the "uniqueID" property but allows specification
        of the access credentials for the database server.

        Parameters
        ----------
        username : str, optional
            DB server access credentials, by default None
        password : str, optional
            DB server access credentials, by default None

        Returns
        -------
        int
            Unique ontology ID.
        """
        return hash(self.getDB_URI(username, password) + self.baseURL)

    @property
    def DB_URI(self):
        """Database URI or database access string that is used to access the database.
        This property never contains the access credentials and thus can be used e.g.,
        to display the access string for verification. Use the "getDB_URI" method
        to generate the propper access string that can be used to connect to the database.

        Returns
        -------
        str
            Database access string without the access credentials.
        """
        return self.__DB_URI.format_map(self)

    def getDB_URI(self, username: str = None, password: str = None):
        """Generates database access string that can be used to connect to the database.
        This string will contain the access credentials (username and password)!

        Parameters
        ----------
        username : str, optional
            DB access credentials (if not provided before), by default None
        password : str, optional
            DB access credentials (if not provided before), by default None

        Returns
        -------
        Literal
            The DB access string.
        """
        if self.DB_URI == self.IN_MEMORY:
            return Literal(self.DB_URI)
        else:
            if username is None:
                if self.__username is None:
                    warn("Username was not set and is not provided when requesting DB URI!", MissingParameterWarning)
                else:
                    username = self.__username
            if password is None:
                if self.__password is None:
                    warn("Password was not set and is not provided when requesting DB URI!", MissingParameterWarning)
                else:
                    password = self.__password

            return Literal(self.DB_URI.format(username=username, password=password))

    def setCredentials(self, username: str = None, password: str = None):
        """Set access credentials for the database server.

        Parameters
        ----------
        username : str, optional
            The username, by default None
        password : str, optional
            The password. Warning, this will be visible in the DB URL! By default None
        """
        self.__username = username
        self.__password = password

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        else:
            return "{" + str(key) + "}"

    @property
    def host(self):
        return self.__host

    @property
    def port(self):
        return self.__port

    @property
    def dialect(self):
        return self.__dialect

    @property
    def driver(self):
        return self.__driver

    @property
    def database(self):
        return self.__database

    @property
    def baseURL(self):
        return self.__baseURL

    @property
    def namespaces(self):
        return self.__namespaces

    def __repr__(self):
        return "\n".join(("{}: {}".format(name, self[name]) for name in dir(self) if not (name.startswith('_') or callable(self[name]))))

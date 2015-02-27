# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

# Defined here to be called from outside the web app
host = 'localhost'
port = '5432'
dbs = ['bod', 'stopo']

class Engines(object):
    def __init__(self, engines={}):
        self.engines = engines

    def get(self, dbname):
        if dbname in self.engines:
            return self.engines[dbname]
        else:
            return None

    def add(self, engine, dbname):
        self.engines[dbname] = engine


class Bases(object):
    def __init__(self):
        self.bases = {}

    def get(self, dbname):
        if dbname in self.bases:
            return self.bases[dbname]
        else:
            return None

    def add(self, engine, dbname):
        base = declarative_base()
        base.metadata.bind = engine
        self.bases[dbname] = base 

engines = Engines()
bases = Bases()

def init():
    for dbname in dbs:
        engine = create_engine('postgresql://%s:%s/%s' %(host, port, dbname))
        engines.add(engine, dbname)
        bases.add(engine, dbname)

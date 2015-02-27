# -*- coding: utf-8 -*-

from sqlalchemy.orm import scoped_session, sessionmaker

from vectorforge.models.stopo import Vec200Namedlocation

DBSession = scoped_session(sessionmaker())

query = DBSession.query(Vec200Namedlocation)
print query.first().id

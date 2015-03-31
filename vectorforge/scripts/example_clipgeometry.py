# -*- coding: utf-8 -*-

from sqlalchemy.orm import scoped_session, sessionmaker
from geoalchemy2.shape import to_shape
from vectorforge.models.stopo import SwissboundariesGemeinde 

DBSession = scoped_session(sessionmaker())

bbox = [550000, 200000, 560000, 210000]
clippedGeometry = SwissboundariesGemeinde.bboxClippedGeom(bbox)
query = DBSession.query(clippedGeometry, SwissboundariesGemeinde.gemname)
query = query.filter(SwissboundariesGemeinde.bboxIntersects(bbox))
print str(query)
for q in query:
    print to_shape(q[0])
    print q[1]

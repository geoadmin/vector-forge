# -*- coding: utf-8 -*-

from vectorforge.lib.boto_s3 import s3Connect, getBucket


conn = s3Connect()
b = getBucket(conn)
for k in b.list():
    k.delete()

# -*- coding: utf-8 -*-

import boto
import geojson
from boto.s3.key import Key


def s3Connect():
    try:
        conn = boto.connect_s3()
    except Exception as e:
        raise e
    return conn


def getBucket(conn):
    try:
        # TODO move S3 bucket name in a config file
        b = conn.get_bucket('wroathiesiuxiefriepl-vectortiles')
    except Exception as e:
        raise e 
    return b


def preparePath(layerId, zoomLevel, tileCol, tileRow, tileFormat='geojson'):
    return '%s/%s/%s/%s.%s' %(layerId, zoomLevel, tileCol, tileRow, tileFormat)


def setFileContent(b, path, featureCollection, contentType='application/json'):
    k = Key(b)
    k.key = path
    return k.set_contents_from_string(geojson.dumps(featureCollection), headers={'Content-Type': contentType})

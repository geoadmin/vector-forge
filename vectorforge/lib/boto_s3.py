# -*- coding: utf-8 -*-

import boto
import geojson
from io import BytesIO
from boto.s3.key import Key


def s3Connect(profileName):
    try:
        conn = boto.connect_s3(profile_name=profileName)
    except Exception as e:
        raise e
    return conn


def getBucket(conn):
    try:
        # TODO move S3 bucket name in a config file
        b = conn.get_bucket('mwks6dv2y5dsbbgg-vectortiles')
    except Exception as e:
        raise e 
    return b


def preparePath(layerId, zoomLevel, tileCol, tileRow, tileFormat='geojson'):
    return '%s/%s/%s/%s.%s' %(layerId, zoomLevel, tileCol, tileRow, tileFormat)


def setFileContent(b, path, featureCollection, contentType='application/json'):
    headers = {'Content-Type': contentType}
    k = Key(b)
    k.key = path
    if isinstance(featureCollection, dict):
        featureCollection = geojson.dumps(featureCollection)
        return k.set_contents_from_string(featureCollection, headers=headers)
    elif isinstance(featureCollection, BytesIO):
        headers['Content-Encoding'] = 'gzip'
        return k.set_contents_from_file(featureCollection, headers=headers)


def writeToS3(b, path, content, origin, bucketBasePath,
        contentType='application/octet-stream', contentEnc='gzip'):
    headers = {'Content-Type': contentType}
    k = Key(b)
    k.key = bucketBasePath + path
    k.set_metadata('IWI_Origin', origin)
    headers['Content-Encoding'] = contentEnc
    headers['Access-Control-Allow-Origin'] = '*'
    k.set_contents_from_file(content, headers=headers)

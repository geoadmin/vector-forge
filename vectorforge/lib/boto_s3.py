# -*- coding: utf-8 -*-

import boto


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

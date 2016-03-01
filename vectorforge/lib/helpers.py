# -*- coding: utf-8 -*-

import time
import datetime
import gzip
import cStringIO


def printProgress(t1, zoom):
    t2 = time.time()
    ti = t2 - t1
    print 'All tiles have been generated for zoom level: %s' % zoom
    print 'It took %s' % str(datetime.timedelta(seconds=ti))


def gzipFileContent(filePath):
    content = open(filePath)
    compressed = cStringIO.StringIO()
    gz = gzip.GzipFile(fileobj=compressed, mode='w')
    gz.writelines(content)
    gz.close()
    compressed.seek(0)
    content.close()
    return compressed


def gzipFileObject(data):
    compressed = cStringIO.StringIO()
    gz = gzip.GzipFile(fileobj=compressed, mode='w', compresslevel=5)
    gz.write(data.getvalue())
    gz.close()
    compressed.seek(0)
    return compressed

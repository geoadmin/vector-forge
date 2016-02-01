# -*- coding: utf-8 -*-

import gzip
import cStringIO


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

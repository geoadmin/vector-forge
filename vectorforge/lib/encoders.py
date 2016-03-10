# -*- coding: utf-8 -*-

import gzip
from io import BytesIO
import cStringIO


def gzippedFileContent(fileName):
    content = open(fileName)
    compressed = cStringIO.StringIO()
    gz = gzip.GzipFile(fileobj=compressed, mode='w')
    gz.writelines(content)
    gz.close()
    content.close()
    return BytesIO(compressed.getvalue())

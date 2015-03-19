# -*- coding: utf-8 -*-

import time
from vectorforge.lib.grid import Grid

zoomLevel = 17
tileCol = 0
tileRow = 0

grid = Grid(zoomLevel)

maxX = grid.maxX
minY = grid.minY

while grid.maxX >= maxX:
    while grid.minY <= minY:
        [minX, minY, maxX, maxY] = grid.tileBounds(tileCol, tileRow)
        print "zoomLevel: %s" %zoomLevel
        print "tileCol: %s" %tileCol
        print "tileRow: %s" %tileRow
        print "[minX, minY, maxX, maxY]: [%s, %s, %s, %s]" %(minX, minY, maxX, maxY)
        time.sleep(1)
        tileRow += 1
    minY = grid.minY
    tileCol += 1
    tileRow = 0
print count

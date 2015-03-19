# -*- coding: utf-8 -*-

## Move in a config file
RESOLUTIONS = [
    4000,
    3750,
    3500,
    3250,
    3000,
    2750,
    2500,
    2250,
    2000,
    1750,
    1500,
    1250,
    1000,
    750,
    650,
    500,
    250,
    100,
    50,
    20,
    10,
    5,
    2.5,
    1.5,
    1,
    0.5,
    0.25,
    0.1
]

MINX = 420000
MAXX = 900000
MINY = 30000
MAXY = 350000

class Grid(object):

    def __init__(self, zoomLevel, tileSizeInPixel=256):
        self.zoomLevel = zoomLevel
        self.tileSizeInPixel = tileSizeInPixel # Square tile only
        self.resolution = RESOLUTIONS[zoomLevel]
        self.origin = [MINX, MAXY] # Top left corner
        self.maxX = MAXX
        self.minY = MINY

    def tileSizeInMeters(self):
        return self.tileSizeInPixel * self.resolution

    def tileBounds(self, tileCol, tileRow):
        minX = self.origin[0] + (tileCol * self.tileSizeInMeters())
        minY = self.origin[1] - ((tileRow + 1) * self.tileSizeInMeters())
        maxX = self.origin[0] + ((tileCol + 1) * self.tileSizeInMeters())
        maxY = self.origin[1] - (tileRow * self.tileSizeInMeters())
        return [minX, minY, maxX, maxY]

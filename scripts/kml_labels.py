import os
import json
import sys
import simplekml
from simplekml import AltitudeMode
from pyproj import Proj, transform


in_proj = Proj(init='epsg:3857')
out_proj = Proj(init='epsg:4326')
FILE_PREFIX = 'ZOOMLEVEL'

# Left keys represent the zoom level in the geojson
# Right vals represent the zoom levels we include to generate the LODS
ZOOM_MAPPING = {
    6: 6,
    7: 7,
    8: 8,
    9: 9,
    10: 10,
    11: 11,
    12: 12,
    13: 13
}

def transform_coordinates(coordinates):
    x, y = transform(in_proj, out_proj, coordinates[0], coordinates[1])
    return [x, y, float(coordinates[2])]


def zoom_to_lod(min_zoom, min_zoom_map, zoom):
    delta = min_zoom - min_zoom_map
    return (zoom - min_zoom + delta)


def valid_coords(coords):
    for c in coords:
        if type(c) != float:
            return False
    return True


def create_schema(kml, lod):
    schema = kml.newschema()
    schema._id = 'kml_schema_ft_%s%s' % (FILE_PREFIX, lod)
    schema.name = '%s%s' %(FILE_PREFIX, lod)
    schema.newsimplefield(name='NAME', type='xsd:string', displayname='NAME')
    schema.newsimplefield(name='UUID', type='xsd:string', displayname='UUID')
    schema.newsimplefield(name='LOD', type='xsd:integer', displayname='LOD')
    schema.newsimplefield(name='LAYERID', type='xsd:float', displayname='LAYERID')
    schema.newsimplefield(name='OBJEKTART', type='xsd:string', displayname='OBJEKTART')
    schema.newsimplefield(name='HOEHE', type='xsd:float', displayname='HOEHE')
    return kml


def escape_chars(txt):
    return txt.replace(u'&', u'&amp;').replace(u'<', u'&lt;').replace(u'>', u'gt;').replace(u'"', u'&quot;').replace(u'\'', u'&apos;')


def main():
    save_folder = '/home/ltgal/data/swissnames/'
    min_zoom = min(ZOOM_MAPPING.keys())
    max_zoom = max(ZOOM_MAPPING.keys())

    min_zoom_map = min(ZOOM_MAPPING.values())

    min_lod = zoom_to_lod(min_zoom, min_zoom_map, min(ZOOM_MAPPING.values()))
    max_lod = zoom_to_lod(min_zoom, min_zoom_map, max(ZOOM_MAPPING.values()))

    if len(sys.argv) != 2:
        print('Please provide a geojson file path')
        sys.exit(1)

    file_path = sys.argv[1]
    if not file_path:
        print('File %s does not exist' % file_path)

    with open(file_path, 'r') as f:
        content = json.load(f)

    features_cache = {}
    features_ids_for_zoom = {}
    for feature in content['features']:
        geometry = feature['geometry']
        geometry_type = geometry['type']
        if geometry_type == 'Point':
            properties = feature['properties']
            uuid = properties['uuid']
            zoom = properties['minzoom'] if properties['minzoom'] > min_zoom else min_zoom
            if zoom <= max_zoom:
                zoom = ZOOM_MAPPING[zoom]
                features_cache[uuid] = feature
                features_ids_for_zoom.setdefault(zoom_to_lod(min_zoom, min_zoom_map, zoom), set())
                features_ids_for_zoom[zoom_to_lod(min_zoom, min_zoom_map, zoom)].add(uuid)

    for lod in range(min_lod, max_lod + 1):
        kml = simplekml.Kml(name='%s%s' %(FILE_PREFIX, lod), visibility=1)
        doc = kml.newdocument()
        fol = doc.newfolder()
        fol._id = 'kml_ft_%s%s' %(FILE_PREFIX, lod)
        kml = create_schema(kml, lod)
        if lod in features_ids_for_zoom:
            for feature_id in list(features_ids_for_zoom[lod]):
                feature = features_cache[feature_id]
                geometry = feature['geometry']
                coordinates = transform_coordinates(geometry['coordinates'])
                name = feature['properties']['name']
                uuid = feature['properties']['uuid']
                layerid = float(feature['properties']['layerid'])
                objektart = feature['properties']['objektart']
                hoehe = float(feature['properties']['hoehe'])
                if type(name) == unicode and type(uuid) == unicode and valid_coords(coordinates) and \
                    type(layerid) == float and type(objektart) == unicode and type(hoehe) == float:
                    pt = fol.newpoint(
                        name=name,
                        coords=[coordinates],
                        altitudemode=AltitudeMode.clamptoground,
                        extrude=0
                    )
                    pt.extendeddata.schemadata.schemaurl = 'kml_schema_ft_%s%s' % (FILE_PREFIX, lod)
                    pt.extendeddata.schemadata.newsimpledata('NAME', escape_chars(name))
                    pt.extendeddata.schemadata.newsimpledata('LOD', lod)
                    pt.extendeddata.schemadata.newsimpledata('UUID', uuid)
                    pt.extendeddata.schemadata.newsimpledata('LAYERID', layerid)
                    pt.extendeddata.schemadata.newsimpledata('OBJEKTART', objektart)
                    pt.extendeddata.schemadata.newsimpledata('HOEHE', hoehe)
                else:
                    print('Skipping uuid %s, name %s, layerid %s, objektart %s, hoehe %s' % (uuid, name, layerid, objektart, hoehe))
                    print(coordinates)
            kml_file = os.path.join(save_folder, '%s%s.kml' % (FILE_PREFIX, lod))
            print('%s features belong to LOD %s' % (len(list(features_ids_for_zoom[lod])), lod))
            print('Saving kml to %s...' % kml_file)
            try:
                kml.save(kml_file)
            except Exception as e:
                print(e)
                print('Could not save %s' % kml_file)


if __name__ == '__main__':
    main()

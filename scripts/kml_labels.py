import os
import json
import sys
import simplekml
import getopt
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
    save_folder = '' 
# /home/ltteo/output/swissnames/20170814'
    file_path = ''
    types = []
    debug = False
    help_msg =  """
kml_labels.py -i <inputfile> -o <outputfolder>'
Options: 
    -i <file path> : Mandatory. Path to a geojson file containing data in swiss coordinates
    -o <output folder path> : Mandatory. Path to a folder where the KMLs will be saved
    -t <object types> : Optional. List of type of objects to export. Ex: 'Ort,Alpiner gipfel,See'
    -d : Optional. Display debug info about skipped features
"""
    try: 
        opts, args = getopt.getopt(sys.argv[1:],"i:o:t:d") 
    except getopt.GetoptError:
        print help_msg
        sys.exit()
    for opt, arg in opts:
        if opt == '-h':
            print help_msg
            sys.exit()
        elif opt in ("-i"):
            file_path = arg
        elif opt in ("-o"):
            save_folder = arg
        elif opt in ("-t"):
            try:
                types = arg.split(',')
            except:
                print 'Bad types parameter' % arg
                print help_msg
                sys.exit()
        elif opt in ("-d"):
            debug = True
    

    
    if not file_path:
        print('Input file %s does not exist' % file_path)
        print help_msg
        sys.exit()

    if not save_folder:
        print('Output folder %s does not exist' % save_folder)
        print help_msg
        sys.exit()


    min_zoom = min(ZOOM_MAPPING.keys())
    max_zoom = max(ZOOM_MAPPING.keys())

    min_zoom_map = min(ZOOM_MAPPING.values())

    min_lod = zoom_to_lod(min_zoom, min_zoom_map, min(ZOOM_MAPPING.values()))
    max_lod = zoom_to_lod(min_zoom, min_zoom_map, max(ZOOM_MAPPING.values()))

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
        nbSkipped = 0
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
                skip = True if not len(types) == 0 else False
                for typee in types:
                    if objektart == typee:
                        skip = False
                        break 
                                         
                if not skip and type(name) == unicode and type(uuid) == unicode and valid_coords(coordinates) and \
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
                    nbSkipped += 1
                    if debug:
                        print('Skipping uuid %s, name %s, layerid %s, objektart %s, hoehe %s' % (uuid, name, layerid, objektart, hoehe))
                        print(coordinates)
            kml_file = os.path.join(save_folder, '%s%s.kml' % (FILE_PREFIX, lod))
            print('%s features belong to LOD %s' % (len(list(features_ids_for_zoom[lod])) - nbSkipped, lod))
            print('Saving kml to %s...' % kml_file)
            try:
                kml.save(kml_file)
            except Exception as e:
                print(e)
                print('Could not save %s' % kml_file)


if __name__ == '__main__':
    main()

import os
import json
import sys
import simplekml
from simplekml import AltitudeMode
from pyproj import Proj, transform

in_proj = Proj(init='epsg:3857')
out_proj = Proj(init='epsg:4326')

def transform_coordinates(coordinates):
    x, y = transform(in_proj, out_proj, coordinates[0], coordinates[1])
    return [x, y, coordinates[2]]


def main():
    save_folder = '/home/ltgal/data/swissnames/'
    min_zoom = 8
    max_zoom = 18

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
            features_cache[uuid] = feature
            features_ids_for_zoom.setdefault(zoom, set())
            features_ids_for_zoom[zoom].add(uuid)

    for zoom in range(min_zoom, max_zoom + 1):
        kml = simplekml.Kml()
        for feature_id in list(features_ids_for_zoom[zoom]):
            feature = features_cache[feature_id]
            geometry = feature['geometry']
            coordinates = transform_coordinates(geometry['coordinates'])
            name = feature['properties']['name']
            kml.newpoint(name=name, coords=[coordinates], altitudemode=AltitudeMode.clamptoground)
        kml.save(os.path.join(save_folder, 'labels_zoom_%s.kml' % zoom))


if __name__ == '__main__':
    main()

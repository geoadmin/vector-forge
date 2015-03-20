$(document).ready(function() {
  var origin = [420000, 350000];
  var defaultResolutions = [4000, 3750, 3500, 3250, 3000, 2750, 2500, 2250,
      2000, 1750, 1500, 1250, 1000, 750, 650, 500, 250, 100, 50, 20, 10, 5,
      2.5, 2, 1.5, 1, 0.5];
  var tileGrid = new ol.tilegrid.WMTS({
    matrixIds: $.map(defaultResolutions, function(r, i) { return i + ''; }),
    origin: origin,
    resolutions: defaultResolutions
  });
  var wmtsGetTileUrlTemplate =
      'http://wmts{5-9}.geo.admin.ch/1.0.0/{Layer}/default/' +
      '{Time}/21781/{TileMatrix}/{TileRow}/{TileCol}.{Format}';
  var getWmtsGetTileUrl = function(layer, format) {
    return wmtsGetTileUrlTemplate
        .replace('{Layer}', layer)
        .replace('{Format}', format);
  };
  var olSource = new ol.source.WMTS({
    dimensions: {
      'Time': '20151231'
    },
    projection: 'EPSG:21781',
    requestEncoding: 'REST',
    tileGrid: tileGrid,
    url: getWmtsGetTileUrl('ch.swisstopo.pixelkarte-farbe', 'jpeg'),
    crossOrigin: 'anonymous'
  });
  olSource.getProjection().setExtent([420000, 30000, 900000, 350000]);
  var olLayer = new ol.layer.Tile({
    source: olSource,
    extent: olSource.getProjection().getExtent()
  });
  var olMap = new ol.Map({
    logo: false,
    controls: ol.control.defaults({
      attributionOptions: {
        collapsible: false
      }
    }),
    layers: [
      olLayer
    ],
    target: 'map',
    view: new ol.View({
      center: [600000, 200000],
      resolution: 650,
      projection: 'EPSG:21781'
    })
  });
});

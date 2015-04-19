$(document).ready(function() {
  var origin = [420000, 350000];
  var extent = [420000, 30000, 900000, 350000];
  var defaultResolutions = [4000, 3750, 3500, 3250, 3000, 2750, 2500, 2250,
      2000, 1750, 1500, 1250, 1000, 750, 650, 500, 250, 100, 50, 20, 10, 5,
      2.5, 2];

  var wmtsGetTileUrlTemplate =
      'http://wmts{5-9}.geo.admin.ch/1.0.0/{Layer}/default/' +
      '{Time}/21781/{TileMatrix}/{TileRow}/{TileCol}.{Format}';
  // TODO add layer reference
  var vectorGetTileUrlTemplate =
      '../../../ogcproxy?url=http://wroathiesiuxiefriepl-vectortiles.s3-website-eu-west-1.amazonaws.com/' +
      '{Layer}/{TileMatrix}/{TileCol}/{TileRow}.{Format}';
  
  var getWmtsGetTileUrl = function(layer, format) {
    return wmtsGetTileUrlTemplate
        .replace('{Layer}', layer)
        .replace('{Format}', format);
  };
  var getVectorGetTileUrl = function(layer, format) {
    return vectorGetTileUrlTemplate
        .replace('{Layer}', layer)
        .replace('{Format}', format);
  };

  var createWMTSGrid = function(resolutions, origin) {
    return new ol.tilegrid.WMTS({
      matrixIds: $.map(resolutions, function(r, i) { return i + ''; }),
      origin: origin,
      resolutions: resolutions
    });
  }

  // WMTS points layer for comparison
  var tileGridComparison = createWMTSGrid(defaultResolutions, origin);
  var olSourceComparison = new ol.source.WMTS({
    dimensions: {
      'Time': '20090401'
    },
    projection: 'EPSG:21781',
    requestEncoding: 'REST',
    tileGrid: tileGridComparison,
    url: getWmtsGetTileUrl('ch.swisstopo.vec25-strassennetz', 'png'),
    crossOrigin: 'anonymous'
  });
  olSourceComparison.getProjection().setExtent(extent);
  var olComparisonLayer = new ol.layer.Tile({
    source: olSourceComparison,
    extent: olSourceComparison.getProjection().getExtent()
  });


  // VECTOR layer
  var tileGrid = createWMTSGrid(defaultResolutions, origin);

  // https://github.com/openlayers/ol3/blob/master/src/ol/source/wmtssource.js
  var createFromWMTSTemplate = function(template) {

    // TODO: we may want to create our own appendParams function so that params
    // order conforms to wmts spec guidance, and so that we can avoid to escape
    // special template params

    // LG: No context for now
    var context = {};
    var dimensions = {};
    var requestEncoding = 'REST';

    template = (requestEncoding == ol.source.WMTSRequestEncoding.KVP) ?
        goog.uri.utils.appendParamsFromMap(template, context) :
        template.replace(/\{(\w+?)\}/g, function(m, p) {
          return (p.toLowerCase() in context) ? context[p.toLowerCase()] : m;
        });

    return (
        /**
         * @param {ol.TileCoord} tileCoord Tile coordinate.
         * @param {number} pixelRatio Pixel ratio.
         * @param {ol.proj.Projection} projection Projection.
         * @return {string|undefined} Tile URL.
         */
        function(tileCoord, pixelRatio, projection) {
          if (goog.isNull(tileCoord)) {
            return undefined;
          } else {
            var localContext = {
              'TileMatrix': tileGrid.getMatrixId(tileCoord[0]),
              'TileCol': tileCoord[1],
              'TileRow': tileCoord[2]
            };
            goog.object.extend(localContext, dimensions);
            var url = template;
            if (requestEncoding == ol.source.WMTSRequestEncoding.KVP) {
              url = goog.uri.utils.appendParamsFromMap(url, localContext);
            } else {
              url = url.replace(/\{(\w+?)\}/g, function(m, p) {
                return localContext[p];
              });
            }
            return url;
          }
        });
  };

  var createTileUrlFunction = function() {
    var tileUrlFunction = ol.TileUrlFunction.nullTileUrlFunction;
    urls = ol.TileUrlFunction.expandUrl(getVectorGetTileUrl('ch.swisstopo.vec25-strassennetz', 'topojson'));
    tileUrlFunction = ol.TileUrlFunction.createFromTileUrlFunctions(
        goog.array.map(urls, createFromWMTSTemplate));
    var tmpExtent = ol.extent.createEmpty();

    return ol.TileUrlFunction.withTileCoordTransform(
        function(tileCoord, projection, opt_tileCoord) {
          goog.asserts.assert(!goog.isNull(tileGrid),
            'tileGrid must not be null');
          if (tileGrid.getResolutions().length <= tileCoord[0]) {
            return null;
          }
          var x = tileCoord[1];
          var y = -tileCoord[2] - 1;
          var tileExtent = tileGrid.getTileCoordExtent(tileCoord, tmpExtent);
          if (!ol.extent.intersects(tileExtent, extent) ||
              ol.extent.touches(tileExtent, extent)) {
            return null;
          }
          return ol.tilecoord.createOrUpdate(tileCoord[0], x, y, opt_tileCoord);
      }, tileUrlFunction);
  };

  var olSourceVector = new ol.source.TileVector({
    format: new ol.format.TopoJSON({
      defaultDataProjection: 'EPSG:21781'
    }),
    projection: 'EPSG:21781',
    requestEncoding: 'REST',
    tileGrid: tileGrid,
    tileUrlFunction: createTileUrlFunction(),
    crossOrigin: 'anonymous',
    extent: extent,
    origin: origin
  });
  olSourceVector.getProjection().setExtent(extent);

  var roadStyles = {
    'Autobahn': new ol.style.Style({stroke: new ol.style.Stroke({color: '#FF9500', width: 2.4})}), 
    'Ein_Ausf': new ol.style.Style({stroke: new ol.style.Stroke({color: '#FFC069', width: 2.1})}),
    '1_Klass': new ol.style.Style({stroke: new ol.style.Stroke({color: '#FF0000', width: 1.9})}),
    '2_Klass': new ol.style.Style({stroke: new ol.style.Stroke({color: '#FAF200', width: 1.6})}),
    '3_Klass': new ol.style.Style({stroke: new ol.style.Stroke({color: '#CCCCCC', width: 1.3})}),
    '4_Klass': new ol.style.Style({stroke: new ol.style.Stroke({color: '#424241', width: 1.0})}),
    '5_Klass': new ol.style.Style({stroke: new ol.style.Stroke({color: '#424241', width: 0.7})}),
    '6_Klass': new ol.style.Style({stroke: new ol.style.Stroke({color: '#CCCCCC', width: 0.4})}),
    'Q_Klass': new ol.style.Style({stroke: new ol.style.Stroke({color: '#CCCCCC', width: 0.1})})
  };

 var olVectorLayer = new ol.layer.Vector({
    source: olSourceVector,
    extent: extent,
    style: function(feature) {
      var val = feature.get('objectval').trim();
      if (roadStyles.hasOwnProperty(val)) {
        return [roadStyles[val]];
      } else {
        return [roadStyles['Q_Klass']];
      }
    }
  });

  olMapToposon = new ol.Map({
    logo: false,
    controls: ol.control.defaults({
      attributionOptions: {
        collapsible: false
      }
    }),
    layers: [
      olVectorLayer
    ],
    target: 'map-toposon',
    view: new ol.View({
      center: [650000, 200000],
      resolution: 10,
      minResolution: 2,
      extent: extent,
      projection: 'EPSG:21781'
    })
  });

  olMapWMTS = new ol.Map({
    logo: false,
    controls: ol.control.defaults({
      attributionOptions: {
        collapsible: false
      }
    }),
    layers: [
      olComparisonLayer
    ],
    target: 'map-wmts',
    view: new ol.View({
      center: [650000, 200000],
      resolution: 10,
      minResolution: 2,
      extent: extent,
      projection: 'EPSG:21781'
    })
  });
  olMapToposon.bindTo('view', olMapWMTS);
});

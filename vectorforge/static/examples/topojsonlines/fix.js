ol.format.TopoJSON.prototype.readFeaturesFromObject = function(
    object, opt_options) {
  // Quick fix
  if (object.arcs.length == 0) {
    return [];
  }
  if (object.type == 'Topology') {
    var topoJSONTopology = /** @type {TopoJSONTopology} */ (object);
    var transform, scale = null, translate = null;
    if (goog.isDef(topoJSONTopology.transform)) {
      transform = /** @type {TopoJSONTransform} */
          (topoJSONTopology.transform);
      scale = transform.scale;
      translate = transform.translate;
    }
    var arcs = topoJSONTopology.arcs;
    if (goog.isDef(transform)) {
      ol.format.TopoJSON.transformArcs_(arcs, scale, translate);
    }
    /** @type {Array.<ol.Feature>} */
    var features = [];
    var topoJSONFeatures = goog.object.getValues(topoJSONTopology.objects);
    var i, ii;
    var feature;
    for (i = 0, ii = topoJSONFeatures.length; i < ii; ++i) {
      if (topoJSONFeatures[i].type === 'GeometryCollection') {
        feature = /** @type {TopoJSONGeometryCollection} */
            (topoJSONFeatures[i]);
        features.push.apply(features,
            ol.format.TopoJSON.readFeaturesFromGeometryCollection_(
                feature, arcs, scale, translate, opt_options));
      } else {
        feature = /** @type {TopoJSONGeometry} */
            (topoJSONFeatures[i]);
        features.push(ol.format.TopoJSON.readFeatureFromGeometry_(
            feature, arcs, scale, translate, opt_options));
      }
    }
    return features;
  } else {
    return [];
  }
};

# Transformer en TopoJSON

CREATE TEMP TABLE edgemap(arc_id serial, edge_id int unique);

SELECT '{ "type": "Topology", "transform": { "scale": [1,1], "translate": [0,0] }, "objects": {';

SELECT '"' || donnees_name || '": ' || topology.AsTopoJSON(topogeom, 'edgemap')
FROM donnees

SELECT '}, "arcs": ['
  UNION ALL
SELECT (regexp_matches(ST_AsGEOJSON(ST_SnapToGrid(e.geom,1)), '\[.*\]'))[1] as t
FROM edgemap m, donnees_topo.edge_data e WHERE e.edge_id = m.edge_id;

SELECT ']}'::text as t

#donnees = vos donnees de depart

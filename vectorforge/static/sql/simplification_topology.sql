#simplification avec POSTGIS topology

select topology.CreateTopology('donnees_topo', find_srid('public', 'donnees', 'geom'));
select topology.AddTopoGeometryColumn('donnees_topo', 'public', 'donnees', 'topogeom', 'MULTIPOLYGON');
UPDATE donnees SET topogeom = topology.toTopoGeom(geom, 'donnees_topo', 1);
SELECT SimplifyEdgeGeom('donnees_topo', edge_id, 10000) FROM donnees_topo.edge;
ALTER TABLE donnees ADD geomsimp GEOMETRY;
UPDATE donnees SET geomsimp = topogeom::geometry;

#donnees = vos donnees de depart

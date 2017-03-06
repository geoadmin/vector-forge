-- ogr2ogr -f "PostgreSQL" PG:"host=pg-0.dev.bgdi.ch dbname=stopo_test_master user=pgkogis" "/home/ltgal/data/swissnames/Labels.json" -nln swissnames3d_labels -append

ALTER TABLE public.swissnames3d_labels RENAME COLUMN wkb_geometry TO the_geom;


-- Table: public.swissnames3d_labels_points

-- DROP TABLE public.swissnames3d_labels_points;

CREATE TABLE public.swissnames3d_labels_points
(
  ogc_fid integer NOT NULL,
  the_geom geometry(Geometry,3857),
  featclass character varying,
  objektart character varying,
  subtype character varying,
  uuid character varying NOT NULL,
  fr character varying,
  name character varying,
  layerid character varying,
  minzoom character varying,
  maxzoom character varying,
  de character varying,
  it character varying,
  endonym character varying,
  roh character varying,
  multi character varying,
  hoehe double precision,
  en character varying,
  CONSTRAINT swissnames3d_labels_points_pkey PRIMARY KEY (ogc_fid)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.swissnames3d_labels_points
  OWNER TO pgkogis;
GRANT ALL ON TABLE public.swissnames3d_labels_points TO pgkogis;
GRANT SELECT ON TABLE public.swissnames3d_labels_points TO "www-data";
GRANT ALL ON TABLE public.swissnames3d_labels_points TO postgres;

-- Index: public.name_points_idx

-- DROP INDEX public.name_points_idx;

CREATE INDEX name_points_idx
  ON public.swissnames3d_labels_points
  USING btree
  (name COLLATE pg_catalog."default");

-- Index: public.objektart_points_idx

-- DROP INDEX public.objektart_points_idx;

CREATE INDEX objektart_points_idx
  ON public.swissnames3d_labels_points
  USING btree
  (objektart COLLATE pg_catalog."default");

-- Index: public.swissnames3d_labels_points_geom_idx

-- DROP INDEX public.swissnames3d_labels_points_geom_idx;

CREATE INDEX swissnames3d_labels_points_geom_idx
  ON public.swissnames3d_labels_points
  USING gist
  (the_geom);

-- Table: public.swissnames3d_labels_lines

-- DROP TABLE public.swissnames3d_labels_lines;

CREATE TABLE public.swissnames3d_labels_lines
(
  ogc_fid integer NOT NULL,
  the_geom geometry(Geometry,3857),
  featclass character varying,
  objektart character varying,
  subtype character varying,
  uuid character varying NOT NULL,
  fr character varying,
  name character varying,
  layerid character varying,
  minzoom character varying,
  maxzoom character varying,
  de character varying,
  it character varying,
  endonym character varying,
  roh character varying,
  multi character varying,
  hoehe double precision,
  en character varying,
  the_geom_topo topogeometry,
  CONSTRAINT swissnames3d_labels_lines_pkey PRIMARY KEY (ogc_fid),
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.swissnames3d_labels_lines
  OWNER TO pgkogis;
GRANT ALL ON TABLE public.swissnames3d_labels_lines TO pgkogis;
GRANT SELECT ON TABLE public.swissnames3d_labels_lines TO "www-data";
GRANT ALL ON TABLE public.swissnames3d_labels_lines TO postgres;

-- Index: public.name_lines_idx

-- DROP INDEX public.name_lines_idx;

CREATE INDEX name_lines_idx
  ON public.swissnames3d_labels_lines
  USING btree
  (name COLLATE pg_catalog."default");

-- Index: public.objektart_lines_idx

-- DROP INDEX public.objektart_lines_idx;

CREATE INDEX objektart_lines_idx
  ON public.swissnames3d_labels_lines
  USING btree
  (objektart COLLATE pg_catalog."default");

-- Index: public.swissnames3d_labels_lines_geom_idx

-- DROP INDEX public.swissnames3d_labels_lines_geom_idx;

CREATE INDEX swissnames3d_labels_lines_geom_idx
  ON public.swissnames3d_labels_lines
  USING gist
  (the_geom);

--- Remove objects for which we don't have a minzoom
DELETE FROM swissnames3d_labels_points WHERE minzoom = '';
DELETE FROM swissnames3d_labels_lines WHERE minzoom = '';

-- Change min/maxzoom types
ALTER TABLE swissnames3d_labels_points
  ALTER COLUMN minzoom TYPE integer USING round(minzoom::float::integer);
ALTER TABLE swissnames3d_labels_points
  ALTER COLUMN maxzoom TYPE integer USING round(maxzoom::float::integer);

ALTER TABLE swissnames3d_labels_lines
  ALTER COLUMN minzoom TYPE integer USING round(minzoom::float::integer);
ALTER TABLE swissnames3d_labels_lines
  ALTER COLUMN maxzoom TYPE integer USING round(maxzoom::float::integer);

INSERT INTO swissnames3d_labels_points SELECT * FROM swissnames3d_labels WHERE ST_GeometryType(the_geom) = 'ST_MultiPoint';
INSERT INTO swissnames3d_labels_lines SELECT * FROM swissnames3d_labels WHERE ST_GeometryType(the_geom) = 'ST_LineString';

-- Create indices

CREATE INDEX minzoom_points_idx
  ON public.swissnames3d_labels_points
  USING btree
  (minzoom);

CREATE INDEX maxzoom_points_idx
  ON public.swissnames3d_labels_points
  USING btree
  (maxzoom);

CREATE INDEX minzoom_lines_idx
  ON public.swissnames3d_labels_lines
  USING btree
  (minzoom);

CREATE INDEX maxzoom_lines_idx
  ON public.swissnames3d_labels_lines
  USING btree
  (maxzoom);

-- Prepare topology
SELECT topology.CreateTopology('topology_swissnames3_labels_lines', 3857);
SELECT topology.AddTopoGeometryColumn('topology_swissnames3_labels_lines', 'public', 'swissnames3d_labels_lines', 'the_geom_topo', 'LINE');

-- Multi to simple geom
ALTER TABLE swissnames3d_labels_points ALTER COLUMN the_geom TYPE geometry(Point, 3857) USING ST_GeometryN(the_geom, 1);

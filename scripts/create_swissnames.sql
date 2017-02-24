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
  tippecanoe character varying,
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
  tippecanoe character varying,
  de character varying,
  it character varying,
  endonym character varying,
  roh character varying,
  multi character varying,
  hoehe double precision,
  en character varying,
  the_geom_topo topogeometry,
  CONSTRAINT swissnames3d_labels_lines_pkey PRIMARY KEY (ogc_fid),
  CONSTRAINT check_topogeom_the_geom_topo CHECK ((the_geom_topo).topology_id = 1 AND (the_geom_topo).layer_id = 1 AND (the_geom_topo).type = 2)
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

INSERT INTO swissnames3d_labels_points SELECT * FROM swissnames3d_labels WHERE ST_GeometryType(the_geom) = 'ST_MultiPoint';
INSERT INTO swissnames3d_labels_lines SELECT * FROM swissnames3d_labels WHERE ST_GeometryType(the_geom) = 'ST_LineString';
SELECT topology.CreateTopology('topology_swissnames3_labels_lines', 3857);
SELECT topology.AddTopoGeometryColumn('topology_swissnames3_labels_lines', 'public', 'swissnames3d_labels_lines', 'the_geom_topo', 'LINE');

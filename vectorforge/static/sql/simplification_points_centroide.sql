/*simplification de donnees type points
methode qui regroupe des points en fonction de la distance et qui cree un point au niveau du centroide*/

create table donnees_simpl as
 SELECT count(geom)::integer AS count, st_centroid(st_collect(geom)) AS center
   FROM donnees
  GROUP BY st_snaptogrid(geom, 5, 5)
  ORDER BY count(geom) DESC;
  
#donnees = vos donnees de depart

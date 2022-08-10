  
select osm_id, count(1) from planet_osm_roads group by osm_id having count(1) > 1;
select * from planet_osm_roads por where osm_id in (select osm_id from (select osm_id, count(1) from planet_osm_roads group by osm_id having count(1) > 1) subsubquery) ;

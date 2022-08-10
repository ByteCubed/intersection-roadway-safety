
SELECT st_transform(ST_PointFromText('POINT(-77.027040 38.925755)', 4326), 3857);
select * from dc.node_intersections ni where st_dwithin(point3857, st_transform(ST_PointFromText('POINT(-77.027040 38.925755)', 4326), 3857), 500);

select * from dc.node_intersections ni where st_dwithin(point3857, st_transform(ST_PointFromText('POINT(-77.001778 38.895857)', 4326), 3857), 1000);
select * from dc.node_intersections ni where st_dwithin(point3857, st_transform(ST_PointFromText('POINT(-76.993672 38.889866)', 4326), 3857), 1500);


select count(1) from dc.node_intersections;
select * from dc.planet_osm_rels where id = 112245;
select * from dc.planet_osm_rels;

select distinct id as rel_id, parts[part_order] as part_id, part_order
from (select id, parts, generate_subscripts(parts, 1) as part_order from dc.planet_osm_rels pow) as foo order by rel_id, part_order;

select * from dc.planet_osm_roads por where osm_id in ('2297230','12724794','968697','1308934','12724795','2297232','2297233','2297231','2297235','2297234','946435','406327','1308936','2295900');

select * from dc.planet_osm_rels por where id in ('2297230','12724794','968697','1308934','12724795','2297232','2297233','2297231','2297235','2297234','946435','406327','1308936','2295900');

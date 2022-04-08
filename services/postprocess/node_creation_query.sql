-- node definition

-- Drop table

-- DROP TABLE node;

CREATE TABLE if not exists node (
	node_id int8 primary KEY,
	point3857 geometry NULL,
	point4326 geometry NULL,
	lat_int int4 NULL,
	long_int int4 NULL,
	on_road bool NULL
);


insert into node
select
	id as node_id, 
	st_transform(st_setsrid(ST_MAKEPOINT(cast(lon as float)/10000000, cast(lat as float)/10000000), 4326), 3857) as point3857, 
	st_setsrid(ST_MAKEPOINT(cast(lon as float)/10000000, cast(lat as float)/10000000), 4326) as point4326, 
	lat as lat_int, 
	lon as long_int 
from planet_osm_nodes pon
on conflict do nothing;


CREATE INDEX IF NOT EXISTS node_index ON node USING gist(point3857);

-- traffic_volume definition

-- Drop table

-- DROP TABLE traffic_volume;

CREATE TABLE if not exists traffic_volume (
	node_id int8,
	ogc_fid int4,
	route_id varchar NULL,
	aadt int4 NULL,
	primary key (node_id, ogc_fid)
);


insert into traffic_volume
select
	distinct ni.node_id,
	ogc_fid,
	tv.route_id,
	aadt
from
	traffic_volume_raw tv
join node_intersections ni on
	ST_DWITHIN(ni.point3857, st_transform(wkb_geometry, 3857), 5) -- collect nodes within 5 meters of the traffic_volume_raw's geometry
where
	aadt > 0 -- ignore areas where we have null or 0 data
on conflict do nothing;


create index if not exists traffic_volume_node_index on traffic_volume(node_id);

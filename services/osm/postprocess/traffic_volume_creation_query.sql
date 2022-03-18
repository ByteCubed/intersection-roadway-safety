-- public.traffic_volume definition

-- Drop table

-- DROP TABLE public.traffic_volume;

CREATE TABLE if not exists public.traffic_volume (
	node_id int8,
	ogc_fid int4,
	routeid varchar NULL,
	aadt int4 NULL,
	primary key (node_id, ogc_fid)
);

insert into traffic_volume
select distinct ni.node_id, ogc_fid, tv.routeid, aadt
from traffic_volume_raw tv
join node_intersections ni on ST_DWITHIN(ni.point3857, st_transform(wkb_geometry, 3857), 5)
where ST_Distance(st_transform(wkb_geometry, 3857), ni.point3857) =
	    (select MIN(ST_Distance(st_transform(wkb_geometry, 3857), subnode.point3857))
	    from node_intersections subnode
	    where ST_DWITHIN(st_transform(wkb_geometry, 3857), subnode.point3857, 5))
    and aadt > 0
    on conflict do nothing;

create index if not exists traffic_volume_node_index on traffic_volume(node_id);
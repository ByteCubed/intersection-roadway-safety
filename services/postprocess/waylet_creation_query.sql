-- waylet definition

-- Drop table

-- DROP TABLE waylet;

CREATE TABLE if not exists waylet (
	waylet_id BIGSERIAL primary key,
	way_id int8 NULL,
	node_id1 int8 NULL,
	node_id2 int8 NULL,
	waylet_line geometry NULL,
	node_order int4 NULL,
	is_road bool NULL,
	highway_type text NULL,
	is_railway bool NULL,
	is_bikepath_or_trail bool NULL,
	is_footway bool NULL,
	way_name text NULL,
	UNIQUE (way_id, node_id1, node_id2)
);

insert into waylet
(way_id, node_id1, node_id2, waylet_line, node_order, is_road, highway_type, is_railway, is_bikepath_or_trail, is_footway, way_name)
select wn1.way_id, wn1.node_id as node_id1, wn2.node_id node_id2, st_makeline(n2.point3857, n1.point3857) as waylet_line, wn1.node_order,
w.is_road, w.highway_type, w.is_railway, w.is_bikepath_or_trail, w.is_footway, way_name
from way_node wn1
join way_node wn2 on wn1.way_id = wn2.way_id
join node n1 on wn1.node_id = n1.node_id
join node n2 on wn2.node_id = n2.node_id
join way w on wn1.way_id = w.way_id
where (wn1.node_order = wn2.node_order + 1)
and (w.is_road or w.is_railway or w.is_bikepath_or_trail or w.is_footway)
and (n1.on_road or n2.on_road)
on conflict do nothing;

CREATE INDEX if not exists waylet_line_idx ON waylet USING gist (waylet_line);
create index if not exists wayletway on waylet(way_id);
create index if not exists wayletnode1 on waylet(node_id1);
create index if not exists wayletnode2 on waylet(node_id2);
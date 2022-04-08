-- way_node definition

-- Drop table

-- DROP TABLE way_node;

CREATE TABLE if not exists way_node (
	way_id int8 NULL,
	node_id int8 null,
	node_order int8 null,
	primary key (way_id, node_id, node_order)
);

insert into way_node
select distinct id as way_id, nodes[node_order] as node_id, node_order
from (select id, nodes, generate_subscripts(nodes, 1) as node_order from planet_osm_ways pow) as foo
ON conflict do nothing;

create index if not exists way_node_way on way_node(way_id);
create index if not exists way_node_node on way_node(node_id);


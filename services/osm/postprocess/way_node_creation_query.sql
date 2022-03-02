-- public.way_node definition

-- Drop table

-- DROP TABLE public.way_node;

CREATE TABLE if not exists public.way_node (
	way_id int8 NULL,
	node_id int8 null,
	primary key (way_id, node_id)
);

insert into way_node
select distinct id as way_id, nodes[node] as node_id
from (select id, nodes, generate_subscripts(nodes, 1) as node from public.planet_osm_ways pow) as foo
ON conflict do nothing;
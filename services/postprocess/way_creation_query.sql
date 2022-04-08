-- way definition

-- Drop table

-- DROP TABLE way;

CREATE TABLE if not exists way (
	way_id int8 primary key,
	way_line geometry NULL,
	nodes _int8 NULL,
	tags _text NULL,
	closed bool NULL,
	is_road bool NULL,
	highway_type text NULL,
	is_railway bool NULL,
	is_bikepath_or_trail bool NULL,
	is_footway bool NULL,
	way_name text NULL
);

insert into way
select way_id, ST_MAKELINE(point3857) as way_line, nodes, tags, case when nodes[1] = nodes[array_upper(nodes,1)] then true else false end as closed from (
select id as way_id, nodes, tags, nodes[node_index] as node_id, n.point3857
from (select id, nodes, tags, generate_subscripts(nodes, 1) as node_index from planet_osm_ways pow) as foo
join node n on foo.nodes[node_index] = n.node_id
order by way_id, node_index asc) subquery
group by way_id, nodes, tags, closed
ON conflict do nothing;

create index if not exists way_index on way(way_id);
create index if not exists way_line_index on way using gist(way_line);

update way w set
is_road = subquery.highway not in ('', 'footway', 'bridleway', 'steps', 'cycleway', 'pedestrian', 'path','raceway', 'rest_area', 'corridor', 'services'),
highway_type = subquery.highway,
is_railway = subquery.railway not in ('', 'abandoned', 'disused', 'subway', 'funicular', 'construction'),
is_bikepath_or_trail = subquery.cycleway not in ('', 'lane', 'shared_lane', 'share_busway', 'no', 'shoulder','opposite_lane') or subquery.route='bicycle' or subquery.highway in ('cycleway','path'),
is_footway = subquery.highway in ('path', 'footway', 'steps') or subquery.footway <> '',
way_name = subquery."name"
from (select way_id, highway, railway, "name", route, footway, cycleway from way_feature_view) subquery
where subquery.way_id = w.way_id;

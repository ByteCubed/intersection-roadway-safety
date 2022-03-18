-- public.node_intersections2 definition

-- Drop table

-- DROP TABLE public.node_intersections;

CREATE TABLE if not exists public.node_intersections (
	node_id int8 primary key,
	point3857 geometry NULL,
	way_lines geometry NULL,
	lat float null,
	long float null,
	way_ids _int8 NULL,
	associatedwayscount int4 NULL,
	legs int null,
	includes_road bool NULL,
	includes_railway bool NULL,
	includes_bikepath bool NULL,
	includes_footway bool NULL
);

insert into node_intersections
select subquery.node_id, subquery.point3857, st_union(subquery.waylet_line) as way_lines, subquery.lat, subquery.long,
array_agg(distinct subquery.way_id) as way_ids, count(distinct subquery.way_id) as associatedwayscount, count(subquery.way_id) as legs,
bool_or(is_road) as includes_road, bool_or(is_railway) as includes_railway, bool_or(is_bikepath_or_trail) as includes_bikepath, bool_or(is_footway) as includes_footway
from (
select n.node_id, n.point3857, w.way_id, w.waylet_line, w.is_road, w.is_railway, w.is_bikepath_or_trail, w.is_footway, cast(n.lat_int as float) / 10000000 as lat, cast(n.long_int as float) / 10000000 as long
from node n
join waylet w on n.node_id = w.node_id1 or n.node_id = w.node_id2
) subquery
group by node_id, point3857, lat, long
having count(subquery.way_id) > 2
ON CONFLICT DO NOTHING;

CREATE INDEX if not exists node_intersections_index ON public.node_intersections USING gist (point3857);

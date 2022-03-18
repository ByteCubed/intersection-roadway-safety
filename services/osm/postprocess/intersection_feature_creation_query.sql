-- public.intersection_features definition

-- Drop table

-- DROP TABLE public.intersection_features;

CREATE TABLE if not exists public.intersection_features (
	node_id int8 NULL,
	way_lines geometry NULL,
	legs int4 NULL,
	nonramp_roads int8 NULL,
	ramp_roads int8 NULL,
	rails int8 NULL,
	bikepaths int8 NULL,
	footways int8 NULL,
	oneways int8 NULL,
	maxspeed text NULL,
	minspeed text NULL,
	sidewalk_count int8 NULL,
	lit _text NULL,
	surface_types _text NULL,
	tunnel int8 NULL,
	tunneltypes _text NULL,
	aadt int8 NULL,
	crashes_within_50 int4 NULL,
	min_angle float8 NULL,
	second_min_angle float8 NULL,
	junction_type int NULL,
	junction_type_list int[] NULL,
	primary key(node_id)
);

insert into public.intersection_features
select
	ni.node_id, ni.way_lines, ni.legs,
	count(1) filter (where w.is_road and highway not in ('trunk_link','secondary_link','primary_link','motorway_link')) as nonramp_roads,
	count(1) filter (where w.is_road and highway in ('trunk_link','secondary_link','primary_link','motorway_link')) as ramp_roads,
	count(1) filter (where w.is_railway) as rails,
	count(1) filter (where w.is_bikepath_or_trail) as bikepaths,
	count(1) filter (where w.is_footway) as footways,
	count(1) filter (where wfv.oneway <> '' and wfv.oneway <> 'no') as oneways,
	max(case when wfv.maxspeed <> '' then wfv.maxspeed end) as maxspeed,
	min(case when wfv.maxspeed <> '' then wfv.maxspeed end) as minspeed,
	sum(case when sidewalk in ('left', 'right') then 1 when sidewalk in ('no', '') then 0 else 2 end) as sidewalk_count,
	array_agg(distinct lit) filter (where lit <> '') as lit,
	array_agg(distinct surface) filter (where surface <> '') as surface_types,
	count(1) filter (where wfv.tunnel <> '') as tunnel,
	array_agg(distinct tunnel) filter (where tunnel <> '') as tunneltypes
from
	node_intersections ni
join waylet w on
	w.node_id1 = ni.node_id or w.node_id2 = ni.node_id
join way_feature_view wfv on
	wfv.way_id = w.way_id
group by
	ni.node_id, ni.way_lines, ni.legs
ON CONFLICT DO NOTHING;

-- add junction type
update
	intersection_features
set
	junction_type =
	case
		when rails > 0 and ramp_roads + nonramp_roads > 0 then 5
		when footways > 0 and ramp_roads + nonramp_roads > 0 then 3
		when bikepaths > 0 and ramp_roads + nonramp_roads > 0 then 4
		when ramp_roads > 0 then 2
		else 1
	end;

-- add junction types as a list for more detail
update intersection_features if2
set junction_type_list = subquery.list
from (
select node_id, array_remove(array_agg(junction_type), null) as list
from (
select node_id, 1 as junction_type from intersection_features if2 where nonramp_roads > 2 UNION
select node_id, 2 as junction_type from intersection_features if2 where ramp_roads > 0 and ramp_roads + nonramp_roads > 2 UNION
select node_id, 3 as junction_type from intersection_features if2 where footways > 0 and ramp_roads + nonramp_roads > 0 UNION
select node_id, 4 as junction_type from intersection_features if2 where bikepaths > 0 and ramp_roads + nonramp_roads > 0 UNION
select node_id, 5 as junction_type from intersection_features if2 where rails > 0 and ramp_roads + nonramp_roads > 0 UNION
select node_id, 6 as junction_type from intersection_features if2 where footways = 0 and bikepaths = 0 and rails = 0 and ramp_roads + nonramp_roads < 3
order by node_id, junction_type) subsubquery
group by node_id) subquery
where if2.node_id = subquery.node_id;

-- update aadt from traffic_volume table
update
	intersection_features xf
set
	aadt = subquery.aadt
from
	(
	select
		ni.node_id,
		max(tv.aadt) as aadt
	from
		node_intersections ni
	join traffic_volume tv on
		ni.node_id = tv.node_id
	group by
		ni.node_id) subquery
where
	subquery.node_id = xf.node_id;

-- update number of crashes from dc crashes
update intersection_features xf
set crashes_within_50 = subquery.crashes_within_50
from (select ni.node_id, count(1) as crashes_within_50
from node_intersections ni join crashes.dc_indexed di on ni.node_id = di.node_id
group by ni.node_id) subquery
where subquery.node_id = xf.node_id;

-- update angle and secondary angle
update intersection_features xf
set min_angle = angle
from (select row_number() over (partition by node_id order by node_id, angle) as num, * from intersection_angle) subquery
where subquery.node_id = xf.node_id and subquery.num=1;

update intersection_features xf
set second_min_angle = angle
from (select row_number() over (partition by node_id order by node_id, angle) as num, * from intersection_angle) subquery
where subquery.node_id = xf.node_id and subquery.num=2;
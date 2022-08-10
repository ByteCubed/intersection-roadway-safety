-- intersection_features definition

-- Drop table

-- DROP TABLE intersection_features;

CREATE TABLE if not exists intersection_features (
	node_id int8 NULL,
	point3857 geometry NULL,
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
	junction_type_id int NULL,
	junction_type_list int[] NULL,
	junction_geometry_type_id int NULL,
	primary key(node_id),
	constraint junction_type foreign key(junction_type_id) references mire.junction_type(junction_type_id),
	constraint junction_geom_type foreign key(junction_geometry_type_id) references mire.junction_geometry_type(junction_geometry_type_id)
);

insert into intersection_features
select
	ni.node_id, ni.point3857, ni.way_lines, ni.legs,
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

-- create point index
create index if not exists intersection_feature_point_index on intersection_features using gist(point3857);

-- add junction type
update
	intersection_features
set
	junction_type_id =
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

-- update angle and secondary angle
update intersection_features xf
set min_angle = angle
from (select row_number() over (partition by node_id order by node_id, angle) as num, * from intersection_angle) subquery
where subquery.node_id = xf.node_id and subquery.num=1;

update intersection_features xf
set second_min_angle = angle
from
	(select row_number() over (partition by node_id order by node_id, angle) as num
		, *
		from intersection_angle) subquery
where subquery.node_id = xf.node_id and subquery.num=2; -- identical to the query above save that it's grabbing the second smallest angle


-- update geometry type
update intersection_features if2 set junction_geometry_type_id = 5
where (select bool_or(junction in ('circular','roundabout')) from curated_way_feature_view cwfv where cwfv.node_id = if2.node_id group by cwfv.node_id) is true;

update intersection_features if2 set junction_geometry_type_id = 1
where junction_geometry_type_id is null and (legs=3 and nonramp_roads = 3 and (min_angle between 70 and 110) and (min_angle + second_min_angle) between 165 and 195);

update intersection_features if2 set junction_geometry_type_id = 2
where  junction_geometry_type_id is null and (legs=3 and nonramp_roads = 3 and not((min_angle between 70 and 110) and (min_angle + second_min_angle) between 165 and 195));

update intersection_features if2 set junction_geometry_type_id = 3
where  junction_geometry_type_id is null and (legs=4 and nonramp_roads + ramp_roads = 3 and second_min_angle - min_angle  < 20);

update intersection_features if2 set junction_geometry_type_id = 4
where  junction_geometry_type_id is null and (legs > 4 and nonramp_roads + ramp_roads > 4);

update intersection_features if2 set junction_geometry_type_id = 7 --'Mid-block crossing'
where nonramp_roads = 2 and footways = 2 and (select count(node_id) from intersection_features if3 where ST_DWITHIN(if3.point3857, if2.point3857, 50) and if3.node_id <> if2.node_id) = 0
and junction_geometry_type_id is null;
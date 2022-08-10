-- Count matched intersections over total. We get 7,053 of their 8191 (86.1%)
select count(distinct case when node_id is not null then oddcpoint end) as ourtotal, count(distinct oddcpoint) as total from (
select
	ST_DISTANCE(if2.point3857, oddcsq.point3857),
	if2.point3857,
	oddcsq.point3857 as oddcpoint,
	node_id,
	ogc_fid
from
	(select
		st_transform(st_setsrid(odi.wkb_geometry, 4326), 3857) as point3857,
		*
	from
		public.opendata_dc_intersections odi where latitude > 38.888611) oddcsq
		left join dc.intersection_features if2 on ST_DWITHIN(if2.point3857, oddcsq.point3857, 15)
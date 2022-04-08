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
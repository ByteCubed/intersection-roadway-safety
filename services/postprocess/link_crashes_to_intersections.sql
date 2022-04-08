alter table crashes add column if not exists node_id int8;

update
	crashes di
set
	node_id = subquery.node_id
from
	(
	select
		di2.objectid,
		n.node_id
	from
		crashes di2
	join node_intersections n on
		ST_DWITHIN(di2.point, n.point3857, 50)
	where
		ST_Distance(di2.point, n.point3857) =
		(select
			MIN(ST_Distance(di2.point, subnode.point3857))
		from
			node_intersections subnode
		where
			ST_DWITHIN(di2.point, subnode.point3857, 50)
		)
      ) subquery
where
	subquery.objectid = di.objectid;

create index if not exists crash_node_id_index on crashes(node_id);

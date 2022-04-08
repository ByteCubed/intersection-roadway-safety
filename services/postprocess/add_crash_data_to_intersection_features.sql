-- update number of crashes from crashes
update intersection_features xf
set crashes_within_50 = subquery.crashes_within_50
from (select ni.node_id, count(1) as crashes_within_50
from node_intersections ni join crashes di on ni.node_id = di.node_id
group by ni.node_id) subquery
where subquery.node_id = xf.node_id;
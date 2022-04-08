update node n
set on_road = subquery.is_road
from (select wn.node_id, w.is_road from way w join way_node wn on w.way_id = wn.way_id) subquery
where subquery.node_id = n.node_id;
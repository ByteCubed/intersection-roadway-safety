-- public.intersection_angle definition

-- Drop table

-- DROP TABLE public.intersection_angle;

CREATE TABLE if not exists public.intersection_angle (
	intersect_angle_id BIGSERIAL primary key,
	node_id int8,
	waylet_id1 int8,
	waylet_id2 int8,
	way_lines public.geometry NULL,
	waylet_line1 public.geometry NULL,
	waylet_line2 public.geometry NULL,
	angle float8 NULL,
	UNIQUE(node_id, waylet_id1, waylet_id2)
);

insert into public.intersection_angle
(node_id, waylet_id1, waylet_id2, way_lines, waylet_line1, waylet_line2, angle)
select ni.node_id, w.waylet_id as waylet_id1, w2.waylet_id as waylet_id2, ni.way_lines,
       w.waylet_line as waylet_line1, w2.waylet_line as waylet_line2, intersect_angle(w.waylet_line, w2.waylet_line) as angle
from node_intersections ni
join waylet w on (ni.node_id = w.node_id1 or ni.node_id = w.node_id2)
join waylet w2 on (ni.node_id = w2.node_id1 or ni.node_id = w2.node_id2) and w2.waylet_id > w.waylet_id
where not (w.node_id1=w2.node_id1 and w.node_id2=w2.node_id2) and not (w.node_id1=w2.node_id2 and w.node_id2=w2.node_id1)
on conflict do nothing;

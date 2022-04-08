create table iowa.crashes as
select cast(-1 as int8) as node_id, st_transform(st_pointfromtext(the_geom, 4326), 3857) as point, *
from iowa.crashes_raw;

create index if not exists iowa_crashes_indexed_point on iowa.crashes using GIST(point);
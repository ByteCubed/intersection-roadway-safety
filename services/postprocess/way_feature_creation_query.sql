-- way_feature definition

-- Drop table

-- DROP TABLE way_feature cascade;

CREATE TABLE if not exists way_feature (
	way_feature_id int8 generated always as identity,
	way_id int8 NULL,
	feature text NULL,
	value text null,
	primary key(way_feature_id)	
);

insert into way_feature (way_id, feature, value)
select foo.id as way_id, foo.tags[s-1] as feature, foo.tags[s] as value  
from (select id, tags, generate_subscripts(tags, 1) as s from planet_osm_ways pow) as foo
left outer join way_feature wf on wf.way_id = foo.id and wf.feature = foo.tags[s-1] and wf.value = foo.tags[s]
where s%2 = 0 and wf.way_feature_id is null
ON conflict do nothing;

create index if not exists way_feature_id_index on way_feature(way_id);


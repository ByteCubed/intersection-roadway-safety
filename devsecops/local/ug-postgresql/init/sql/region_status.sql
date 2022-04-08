CREATE TABLE if not exists public.region_state (
	region_state_id int primary key,
	description text
);

insert into region_state values
(1, 'SCHEMA CREATED'),
(2, 'POSTGRES PREINGEST COMPLETE'),
(3, 'CRASHES LOADED'),
(4, 'TRAFFIC_VOLUME LOADED'),
(5, 'POSTGRES POSTPROCESS COMPLETE'),
(6, 'OSM STARTED'),
(7, 'OSM POSTPROCESS STARTED'),
(8, 'OSM POSTPROCESS COMPLETE'),
(9, 'SAT_IMAGE PROCESSING STARTED'),
(10, 'SAT_IMAGE PROCESSING COMPLETE');

CREATE TABLE if not exists public.region_status (
	region_name text primary key,
	region_state_id int,
	constraint fk_region_state foreign key (region_state_id) references region_state(region_state_id)
);
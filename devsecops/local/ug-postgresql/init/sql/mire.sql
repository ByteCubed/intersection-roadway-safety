CREATE SCHEMA mire;

CREATE TABLE mire.attribute_set
(
  id SERIAL NOT NULL UNIQUE ,
  name VARCHAR(256),
  CONSTRAINT attribute_set_pkey PRIMARY KEY (id)
);

CREATE TABLE mire.attribute_type
(
  id SERIAL NOT NULL UNIQUE ,
  name VARCHAR(256),
  CONSTRAINT attribute_type_pkey PRIMARY KEY (id)
);

CREATE TABLE mire.attribute
(
  id SERIAL NOT NULL UNIQUE ,
  attribute_set_id INTEGER,
  attribute_type_id INTEGER,
  name VARCHAR(256),
  CONSTRAINT attribute_pkey PRIMARY KEY (id)
);

CREATE TABLE mire.element_attribute
(
  element_id INTEGER,
  attribute_id INTEGER
);

CREATE TABLE mire.element_flag
(
  id SERIAL NOT NULL UNIQUE ,
  name VARCHAR(256),
  CONSTRAINT element_flag_pkey PRIMARY KEY (id)
);

CREATE TABLE mire.element_element_flag
(
  element_id INTEGER,
  element_flag_id INTEGER
);

CREATE TABLE mire.section
(
  id SERIAL NOT NULL UNIQUE ,
  name VARCHAR(256),
  CONSTRAINT section_pkey PRIMARY KEY (id)
);

CREATE TABLE mire.element
(
  id SERIAL NOT NULL UNIQUE ,
  section_id INTEGER,
  name VARCHAR(256),
  definition TEXT,
  CONSTRAINT element_pkey PRIMARY KEY (id)
);

ALTER TABLE mire.attribute ADD FOREIGN KEY (attribute_set_id) REFERENCES mire.attribute_set (id);

ALTER TABLE mire.attribute ADD FOREIGN KEY (attribute_type_id) REFERENCES mire.attribute_type (id);

ALTER TABLE mire.element_attribute ADD FOREIGN KEY (element_id) REFERENCES mire.element (id);

ALTER TABLE mire.element_attribute ADD FOREIGN KEY (attribute_id) REFERENCES mire.attribute (id);

ALTER TABLE mire.element_element_flag ADD FOREIGN KEY (element_id) REFERENCES mire.element (id);

ALTER TABLE mire.element_element_flag ADD FOREIGN KEY (element_flag_id) REFERENCES mire.element_flag (id);

ALTER TABLE mire.element ADD FOREIGN KEY (section_id) REFERENCES mire.section (id);


COPY mire.section(
  id
  ,name
)
FROM
  '/data/mire/section.csv'
WITH
  CSV HEADER
;

COPY mire.element_flag(
  id
  ,name
)
FROM
  '/data/mire/element_flag.csv'
WITH
  CSV HEADER
;

COPY mire.element(
  id
  ,section_id
  ,name
  ,definition
)
FROM
  '/data/mire/element.csv'
WITH
  CSV HEADER
;

COPY mire.element_element_flag(
  element_id
  ,element_flag_id
)
FROM
  '/data/mire/element_element_flag.csv'
WITH
  CSV HEADER
;


-- mire.junction_geometry_type definition

-- Drop table

-- DROP TABLE mire.junction_geometry_type;

CREATE TABLE mire.junction_geometry_type (
	junction_geometry_type_id int4 NOT NULL,
	description text NULL,
	CONSTRAINT junction_geometry_type_pkey PRIMARY KEY (junction_geometry_type_id)
);

insert into mire.junction_geometry_type (junction_geometry_type_id, description) values
(1, 'T-Intersection'),
(2, 'Y-Intersection'),
(3, 'Cross Intersection'),
(4, '5 or more legs and not circular'),
(5, 'Roundabout'),
(6, 'Other Circular Intersection including rotaries and neighborhood traffic circles'),
(7, 'Midblock Pedestrian Crossing'),
(8, 'Restricted Crossing U-turn intersection'),
(9, 'Median U-turn intersection'),
(10, 'Displaced left-turn intersection'),
(11, 'Jughandle intersection'),
(12, 'Continuous green T intersection'),
(13, 'Quadrant intersection'),
(14, 'Other');

-- mire.junction_type definition

-- Drop table

-- DROP TABLE mire.junction_type;

CREATE TABLE mire.junction_type (
	junction_type_id int4 NOT NULL,
	description text NULL,
	CONSTRAINT junction_type_pkey PRIMARY KEY (junction_type_id)
);

insert into mire.junction_type (junction_type_id, description) values
(1, 'Roadway/roadway (not interchange related)'),
(2, 'Roadway/roadway (interchange ramp terminal)'),
(3, 'Roadway/pedestrian crossing'),
(4, 'Roadway/bicycle path or trail'),
(5, 'Roadway/railroad grade crossing'),
(6, 'Other');
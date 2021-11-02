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
  '/tmp/mire/section.csv'
WITH
  CSV HEADER
;

COPY mire.element_flag(
  id
  ,name
)
FROM
  '/tmp/mire/element_flag.csv'
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
  '/tmp/mire/element.csv'
WITH
  CSV HEADER
;

COPY mire.element_element_flag(
  element_id
  ,element_flag_id
)
FROM
  '/tmp/mire/element_element_flag.csv'
WITH
  CSV HEADER
;

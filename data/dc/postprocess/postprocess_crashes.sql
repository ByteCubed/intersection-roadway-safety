select *,  ST_Transform(ST_SetSRID(ST_MakePoint(cast(longitude as float),cast(latitude as float)), 4326),3857) as point into dc.crashes from dc.crashes_raw;

CREATE INDEX IF NOT EXISTS dc_crashes_indexed_point ON dc.crashes USING gist(point);
-- In the subquery, copy the coords from the json.
-- You can add an arbitrary number of "union select <coords>", but it may run more slowly at high counts.
-- Initial coords are for DC.

select st_transform(st_setsrid(st_makepolygon(ST_GEOMFROMTEXT('LINESTRING(' || east || ' ' || north || ',' ||
west || ' ' || north || ',' ||
west || ' ' || south || ',' ||
east || ' ' || south || ',' ||
east || ' ' || north || ')'
)),4326),3857) from
(select 38.9 as north, 38.9 as south, -77 as east, -77 as west
-- union select
) sq;
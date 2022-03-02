-- public.intersection_xsect definition

-- Drop table

-- DROP TABLE public.intersection_xsect;

CREATE TABLE if not exists public.intersection_xsect (
	intersection_xsect_id int8 generated always as identity,
	osm_id1 int8 NULL,
	osm_id2 int8 NULL,
	xsect geometry NULL,
	way1 geometry(linestring, 3857) NULL,
	way2 geometry(linestring, 3857) NULL,
	count int8 NULL,
	angle float8 null,
	primary key(intersection_xsect_id)
);

insert into intersection_xsect (osm_id1, osm_id2, xsect, way1, way2, count, angle)
select
    a.osm_id as osm_id1,
    b.osm_id as osm_id2, 
    ST_Intersection(a.way, b.way) as xsect,
    a.way as way1,
    b.way as way2,
    Count(Distinct a.osm_id),
    least(degrees(ST_Angle(a.way, b.way)), 360 - degrees(ST_Angle(a.way, b.way))) as angle
FROM
    rws.public.planet_osm_roads as a join rws.public.planet_osm_roads as b on ST_Touches(a.way, b.way) AND a.osm_id > b.osm_id
WHERE
    ( (a.bridge not like 'yes' or a.bridge is null ) or
    (b.bridge not like 'yes' or b.bridge is null ))    
    AND degrees( ST_Angle(a.way, b.way) ) > 25 and degrees( ST_Angle(a.way, b.way) ) < 335 -- no 0 or 360 degree angles
    and not ( degrees( ST_Angle(a.way, b.way) ) < 205 and degrees( ST_Angle(a.way, b.way) ) > 155) --no 180 degree angles
    and a.highway is not null and b.highway is not null
GROUP BY
    ST_Intersection(a.way, b.way),
    a.osm_id,
    b.osm_id, 
    a.way,
    b.way;
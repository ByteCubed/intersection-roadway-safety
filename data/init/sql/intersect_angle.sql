CREATE OR REPLACE FUNCTION public.intersect_angle(line1 geometry, line2 geometry)
 RETURNS double precision
 LANGUAGE plpgsql
AS $function$
    declare angle float;
    begin
	   select abs(degrees( ST_Azimuth ( st_geometryn(ST_Intersection(line1, line2), 1), ST_LineInterpolatePoint( line1, abs(ST_LineLocatePoint(line1, st_geometryn(ST_Intersection(line1, line2), 1)) - 0.0001) ) ) - ST_Azimuth ( st_geometryn(ST_Intersection(line1, line2), 1), ST_LineInterpolatePoint( line2, abs(ST_LineLocatePoint(line2, st_geometryn(ST_Intersection(line1, line2), 1)) - 0.0001) ) )))
	   into angle;
	   if angle > 180.0 THEN
	        angle := 360 - angle;
       end if;
       return angle;
    end
    $function$
;

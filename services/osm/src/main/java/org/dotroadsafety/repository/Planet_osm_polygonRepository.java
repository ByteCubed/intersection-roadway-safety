package org.dotroadsafety.repository;

import org.dotroadsafety.model.Planet_osm_point;
import org.dotroadsafety.model.Planet_osm_polygon;
import org.springframework.data.jdbc.repository.query.Query;
import org.springframework.data.repository.PagingAndSortingRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface Planet_osm_polygonRepository extends PagingAndSortingRepository<Planet_osm_polygon, Long> {

    @Query(value = "SELECT * FROM planet_osm_polygon WHERE name= :name;")
    Iterable<Planet_osm_polygon> findPolygonsByName(@Param("name") String name);

    @Query(value = "SELECT * FROM planet_osm_polygon WHERE name LIKE CONCAT('%',:name,'%');")
    Iterable<Planet_osm_polygon> findPolygonsLikeName(@Param("name") String name);
}


package org.dotroadsafety.repository;

import org.apache.lucene.spatial3d.geom.Plane;
import org.dotroadsafety.model.Planet_osm_line;
import org.dotroadsafety.model.Planet_osm_point;
import org.springframework.data.jdbc.repository.query.Query;
import org.springframework.data.repository.PagingAndSortingRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface Planet_osm_pointRepository extends PagingAndSortingRepository<Planet_osm_point, Long> {

    @Query(value = "SELECT * FROM planet_osm_point WHERE name= :name;")
    Iterable<Planet_osm_point> findPointsByName(@Param("name") String name);

    @Query(value = "SELECT * FROM planet_osm_point WHERE name LIKE CONCAT('%',:name,'%');")
    Iterable<Planet_osm_point> findPointsLikeName(@Param("name") String name);
}

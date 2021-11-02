package org.dotroadsafety.repository;

import org.apache.lucene.spatial3d.geom.Plane;
import org.dotroadsafety.model.Planet_osm_roads;
import org.elasticsearch.search.aggregations.metrics.InternalHDRPercentiles;
import org.springframework.data.jdbc.repository.query.Query;
import org.springframework.data.repository.PagingAndSortingRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface Planet_osm_roadsRepository extends PagingAndSortingRepository<Planet_osm_roads, Long> {

    @Query(value = "SELECT * FROM planet_osm_roads WHERE name= :name;")
    Iterable<Planet_osm_roads> findAllRoadsByName(@Param("name") String name);

    @Query(value = "SELECT * FROM planet_osm_roads WHERE name LIKE CONCAT('%',:name,'%');")
    Iterable<Planet_osm_roads> findRoadsLikeName(@Param("name") String name);
}

package org.dotroadsafety.repository;

import org.dotroadsafety.model.Planet_osm_line;
import org.dotroadsafety.model.Planet_osm_roads;
import org.springframework.data.jdbc.repository.query.Query;
import org.springframework.data.repository.PagingAndSortingRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface Planet_osm_lineRepository extends PagingAndSortingRepository<Planet_osm_line, Long> {
    @Query(value = "SELECT * FROM planet_osm_line WHERE name= :name;")
    Iterable<Planet_osm_line> findAllLinesByName(@Param("name") String name);

    @Query(value = "SELECT * FROM planet_osm_line WHERE name LIKE CONCAT('%',:name,'%');")
    Iterable<Planet_osm_line> findLinesLikeName(@Param("name") String name);
}

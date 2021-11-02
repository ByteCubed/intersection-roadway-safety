package org.dotroadsafety.repository;

import org.dotroadsafety.model.Planet_osm_polygon;
import org.dotroadsafety.model.Planet_osm_roads;
import org.dotroadsafety.model.Spatial_ref_sys;
import org.springframework.data.jdbc.repository.query.Query;
import org.springframework.data.repository.PagingAndSortingRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface Spatial_ref_sysRepository extends PagingAndSortingRepository<Spatial_ref_sys, Long> {

    @Query(value = "SELECT * FROM spatial_ref_sys WHERE name= :name;")
    Iterable<Spatial_ref_sys> findSpatialRefsByName(@Param("name") String name);

    @Query(value = "SELECT * FROM spatial_ref_sys WHERE name LIKE CONCAT('%',:name,'%');")
    Iterable<Spatial_ref_sys> findSpatialRefsLikeName(@Param("name") String name);
}

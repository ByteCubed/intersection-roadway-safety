package org.dotroadsafety.repository;

import org.dotroadsafety.model.Crashes;
import org.dotroadsafety.model.Planet_osm_roads;
import org.springframework.data.jdbc.repository.query.Query;
import org.springframework.data.repository.PagingAndSortingRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface CrashesRepository extends  PagingAndSortingRepository<Crashes, Long> {


    @Query(value = "SELECT * FROM crashes WHERE address= :address;")
    Iterable<Crashes> findAllCrashesByAddress(@Param("address") String address);

    @Query(value = "SELECT * FROM crashes WHERE crimeid= :crimeId;")
    Iterable<Crashes> findByCrimeID(String crimeId);
}

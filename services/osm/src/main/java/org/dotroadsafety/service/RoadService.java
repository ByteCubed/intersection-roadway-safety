package org.dotroadsafety.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.dotroadsafety.model.Planet_osm_roads;
import org.dotroadsafety.repository.Planet_osm_roadsRepository;
import org.elasticsearch.client.RestHighLevelClient;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class RoadService {

    @Autowired
    Planet_osm_roadsRepository planet_osm_roadsRepository;

    public Planet_osm_roads findRoadById(Long osmId) {
        Optional<Planet_osm_roads> roads = planet_osm_roadsRepository.findById(osmId);
        return roads.get();
    }

    public Iterable<Planet_osm_roads> findRoadsByName(String roadName) {
        return planet_osm_roadsRepository.findAllRoadsByName(roadName);
    }

    public Iterable<Planet_osm_roads> findRoadsLikeName(String roadName) {
        return planet_osm_roadsRepository.findRoadsLikeName(roadName);
    }

    public Iterable<Planet_osm_roads> findAllRoadsWithPaging(int pageSize) {
        return planet_osm_roadsRepository.findAll(Pageable.ofSize(pageSize));
    }

    public Iterable<Planet_osm_roads> findAllRoadsByPageAndSize(int pageNumber, int pageSize) {
        return planet_osm_roadsRepository.findAll(PageRequest.of(pageNumber, pageSize));
    }

    public Iterable<Planet_osm_roads> findAllRoads() {
        return planet_osm_roadsRepository.findAll();
    }

}

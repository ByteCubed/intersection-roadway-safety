package org.dotroadsafety.service;

import org.dotroadsafety.model.Planet_osm_polygon;
import org.dotroadsafety.repository.Planet_osm_polygonRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class PolygonService {

    @Autowired
    Planet_osm_polygonRepository polygonRepository;

    public Planet_osm_polygon findPolygonById(Long osmId) {
        Optional<Planet_osm_polygon> Polygons = polygonRepository.findById(osmId);
        return Polygons.get();
    }

    public Iterable<Planet_osm_polygon> findPolygonsByName(String roadName) {
        return polygonRepository.findPolygonsByName(roadName);
    }

    public Iterable<Planet_osm_polygon> findPolygonsLikeName(String roadName) {
        return polygonRepository.findPolygonsLikeName(roadName);
    }

    public Iterable<Planet_osm_polygon> findAllPolygonsWithPaging(int pageSize) {
        return polygonRepository.findAll(Pageable.ofSize(pageSize));
    }

    public Iterable<Planet_osm_polygon> findAllPolygonsByPageAndSize(int pageNumber, int pageSize) {
        return polygonRepository.findAll(PageRequest.of(pageNumber, pageSize));
    }

    public Iterable<Planet_osm_polygon> findAllPolygons() {
        return polygonRepository.findAll();
    }

}

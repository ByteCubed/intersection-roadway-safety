package org.dotroadsafety.service;

import org.dotroadsafety.model.Planet_osm_point;
import org.dotroadsafety.repository.Planet_osm_pointRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class PointService {

    @Autowired
    Planet_osm_pointRepository pointRepository;

    public Planet_osm_point findPointById(Long osmId) {
        Optional<Planet_osm_point> Points = pointRepository.findById(osmId);
        return Points.get();
    }

    public Iterable<Planet_osm_point> findPointsByName(String roadName) {
        return pointRepository.findPointsByName(roadName);
    }

    public Iterable<Planet_osm_point> findPointsLikeName(String roadName) {
        return pointRepository.findPointsLikeName(roadName);
    }

    public Iterable<Planet_osm_point> findAllPointsWithPaging(int pageSize) {
        return pointRepository.findAll(Pageable.ofSize(pageSize));
    }

    public Iterable<Planet_osm_point> findAllPointsByPageAndSize(int pageNumber, int pageSize) {
        return pointRepository.findAll(PageRequest.of(pageNumber, pageSize));
    }

    public Iterable<Planet_osm_point> findAllPoints() {
        return pointRepository.findAll();
    }

}

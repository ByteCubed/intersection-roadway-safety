package org.dotroadsafety.service;

import org.dotroadsafety.model.Planet_osm_line;
import org.dotroadsafety.model.Planet_osm_roads;
import org.dotroadsafety.repository.Planet_osm_lineRepository;
import org.dotroadsafety.repository.Planet_osm_roadsRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class LineService {

    @Autowired
    Planet_osm_lineRepository planet_osm_lineRepository;

    public Planet_osm_line findLineById(Long osmId) {
        Optional<Planet_osm_line> lines = planet_osm_lineRepository.findById(osmId);
        return lines.get();
    }

    public Iterable<Planet_osm_line> findLinesByName(String roadName) {
        return planet_osm_lineRepository.findAllLinesByName(roadName);
    }

    public Iterable<Planet_osm_line> findLinesLikeName(String roadName) {
        return planet_osm_lineRepository.findLinesLikeName(roadName);
    }

    public Iterable<Planet_osm_line> findAllLinesWithPaging(int pageSize) {
        return planet_osm_lineRepository.findAll(Pageable.ofSize(pageSize));
    }

    public Iterable<Planet_osm_line> findAllLinesByPageAndSize(int pageNumber, int pageSize) {
        return planet_osm_lineRepository.findAll(PageRequest.of(pageNumber, pageSize));
    }

    public Iterable<Planet_osm_line> findAllLines() {
        return planet_osm_lineRepository.findAll();
    }

}

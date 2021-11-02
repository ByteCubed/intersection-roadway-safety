package org.dotroadsafety.controller;

import org.dotroadsafety.model.Planet_osm_line;
import org.dotroadsafety.model.Planet_osm_point;
import org.dotroadsafety.service.PointService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController()
@RequestMapping("/dot-road-safety")
public class PointController {

    @Autowired
    private final PointService pointService;

    public PointController(PointService pointService) {
        this.pointService = pointService;
    }

    @GetMapping("/points/all")
    public Iterable<Planet_osm_point> getAllLines() {
        return pointService.findAllPoints();
    }

    @GetMapping("/points/page={pageNumber}/size={pageSize}")
    public Iterable<Planet_osm_point> getAllPointsByPageAndSize(@PathVariable int pageNumber, @PathVariable int pageSize) {
        return pointService.findAllPointsByPageAndSize(pageNumber, pageSize);
    }

    @GetMapping("/points/{osmId}")
    public Planet_osm_point getPointByOsmID(@PathVariable Long osmId) {
        return pointService.findPointById(osmId);
    }

    @GetMapping("/points/by-name/{pointName}")
    public Iterable<Planet_osm_point> getPointsByName(@PathVariable String pointName) {
        return pointService.findPointsByName(pointName);
    }

    @GetMapping("/points/like-name/{pointName}")
    public Iterable<Planet_osm_point> getPointsLikeName(@PathVariable String pointName) {
        return pointService.findPointsLikeName(pointName);
    }
}

package org.dotroadsafety.controller;

import org.dotroadsafety.model.Planet_osm_roads;
import org.dotroadsafety.service.RoadService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController()
@RequestMapping("/dot-road-safety")
public class RoadsController {

    @Autowired
    private final RoadService roadService;

    public RoadsController(RoadService roadService) {
        this.roadService = roadService;
    }

    @GetMapping("/roads/all")
    public Iterable<Planet_osm_roads> getAllRoads() {
        return roadService.findAllRoads();
    }

    @GetMapping("/roads/page={pageNumber}/size={pageSize}")
    public Iterable<Planet_osm_roads> getAllRoadsByPageAndSize(@PathVariable int pageNumber, @PathVariable int pageSize) {
        return roadService.findAllRoadsByPageAndSize(pageNumber, pageSize);
    }

    @GetMapping("/roads/{osmId}")
    public Planet_osm_roads getRoadsByOsmID(@PathVariable Long osmId) {
        return roadService.findRoadById(osmId);
    }

    @GetMapping("/roads/by-name/{roadName}")
    public Iterable<Planet_osm_roads> getRoadsByName(@PathVariable String roadName) {
        return roadService.findRoadsByName(roadName);
    }

    @GetMapping("/roads/like-name/{roadName}")
    public Iterable<Planet_osm_roads> getRoadsLikeName(@PathVariable String roadName) {
        return roadService.findRoadsLikeName(roadName);
    }
}

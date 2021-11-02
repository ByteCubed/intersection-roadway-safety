package org.dotroadsafety.controller;

import org.dotroadsafety.model.Planet_osm_polygon;
import org.dotroadsafety.service.PolygonService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController()
@RequestMapping("/dot-road-safety")
public class PolygonController {

    @Autowired
    private final PolygonService polygonService;

    public PolygonController(PolygonService polygonService) {
        this.polygonService = polygonService;
    }

    @GetMapping("/polygons/all")
    public Iterable<Planet_osm_polygon> getAllPolygons() {
        return polygonService.findAllPolygons();
    }

    @GetMapping("/polygons/page={pageNumber}/size={pageSize}")
    public Iterable<Planet_osm_polygon> getAllPolygonsByPageAndSize(@PathVariable int pageNumber, @PathVariable int pageSize) {
        return polygonService.findAllPolygonsByPageAndSize(pageNumber, pageSize);
    }

    @GetMapping("/polygons/{osmId}")
    public Planet_osm_polygon getPolygonByOsmID(@PathVariable Long osmId) {
        return polygonService.findPolygonById(osmId);
    }

    @GetMapping("/polygons/by-name/{polygonName}")
    public Iterable<Planet_osm_polygon> getPolygonsByName(@PathVariable String polygonName) {
        return polygonService.findPolygonsByName(polygonName);
    }

    @GetMapping("/polygons/like-name/{polygonName}")
    public Iterable<Planet_osm_polygon> getPolygonsLikeName(@PathVariable String polygonName) {
        return polygonService.findPolygonsLikeName(polygonName);
    }
}

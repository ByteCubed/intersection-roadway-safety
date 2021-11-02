package org.dotroadsafety.controller;

import org.dotroadsafety.model.Spatial_ref_sys;
import org.dotroadsafety.service.SpatialRefService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController()
@RequestMapping("/dot-road-safety")
public class SpatialRefController {

    @Autowired
    private final SpatialRefService spatialRefService;

    public SpatialRefController(SpatialRefService spatialRefService) {
        this.spatialRefService = spatialRefService;
    }

    @GetMapping("/spatialref/all")
    public Iterable<Spatial_ref_sys> getAllSpatialRefs() {
        return spatialRefService.findAllSpatialRefs();
    }

    @GetMapping("/spatialref/page={pageNumber}/size={pageSize}")
    public Iterable<Spatial_ref_sys> getAllSpatialRefByPageAndSize(@PathVariable int pageNumber, @PathVariable int pageSize) {
        return spatialRefService.findAllSpatialRefsByPageAndSize(pageNumber, pageSize);
    }

    @GetMapping("/spatialref/{osmId}")
    public Spatial_ref_sys getSpatialRefByOsmID(@PathVariable Long osmId) {
        return spatialRefService.findSpatialRefById(osmId);
    }

    @GetMapping("/spatialref/by-name/{spatialRefName}")
    public Iterable<Spatial_ref_sys> getSpatialRefByName(@PathVariable String spatialRefName) {
        return spatialRefService.findSpatialRefsByName(spatialRefName);
    }

    @GetMapping("/spatialref/like-name/{spatialRefName}")
    public Iterable<Spatial_ref_sys> getSpatialRefLikeName(@PathVariable String spatialRefName) {
        return spatialRefService.findSpatialRefsLikeName(spatialRefName);
    }
}

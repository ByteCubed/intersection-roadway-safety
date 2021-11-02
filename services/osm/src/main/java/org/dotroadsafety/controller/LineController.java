package org.dotroadsafety.controller;

import org.dotroadsafety.model.Planet_osm_line;
import org.dotroadsafety.service.LineService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController()
@RequestMapping("/dot-road-safety")
public class LineController {

    @Autowired
    private final LineService lineService;

    public LineController(LineService lineService) {
        this.lineService = lineService;
    }

    @GetMapping("/lines/all")
    public Iterable<Planet_osm_line> getAllLines() {
        return lineService.findAllLines();
    }

    @GetMapping("/lines/page={pageNumber}/size={pageSize}")
    public Iterable<Planet_osm_line> getAllLinesByPageAndSize(@PathVariable int pageNumber, @PathVariable int pageSize) {
        return lineService.findAllLinesByPageAndSize(pageNumber, pageSize);
    }

    @GetMapping("/lines/{osmId}")
    public Planet_osm_line getLineByOsmID(@PathVariable Long osmId) {
        return lineService.findLineById(osmId);
    }

    @GetMapping("/lines/by-name/{lineName}")
    public Iterable<Planet_osm_line> getLinesByName(@PathVariable String lineName) {
        return lineService.findLinesByName(lineName);
    }

    @GetMapping("/lines/like-name/{lineName}")
    public Iterable<Planet_osm_line> getLinesLikeName(@PathVariable String lineName) {
        return lineService.findLinesLikeName(lineName);
    }
}

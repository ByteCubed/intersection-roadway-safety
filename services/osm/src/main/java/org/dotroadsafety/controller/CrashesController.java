package org.dotroadsafety.controller;

import org.dotroadsafety.model.Crashes;
import org.dotroadsafety.model.Planet_osm_roads;
import org.dotroadsafety.service.CrashesService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController()
@RequestMapping("/dot-road-safety")
public class CrashesController {

    @Autowired
    private final CrashesService crashesService;

    public CrashesController(CrashesService crashesService) {
        this.crashesService = crashesService;
    }

    @GetMapping("/crashes/all")
    public Iterable<Crashes> getAllCrashes() {
        return crashesService.findAllCrashes();
    }

    @GetMapping("/crashes/page={pageNumber}/size={pageSize}")
    public Iterable<Crashes> getAllCrashesByPageAndSize(@PathVariable int pageNumber, @PathVariable int pageSize) {
        return crashesService.findAllCrashesByPageAndSize(pageNumber, pageSize);
    }

    @GetMapping("/crashes/{uid}")
    public Crashes getCrashesByUid(@PathVariable Long uid) {
        return crashesService.findCrashById(uid);
    }

    @GetMapping("/crashes/like-name/{crimeId}")
    public Iterable<Crashes> getCrashesByCrimeId(@PathVariable String crimeId) {
        return crashesService.findCrashesByCrimeId(crimeId);
    }
}

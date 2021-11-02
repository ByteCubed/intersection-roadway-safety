package org.dotroadsafety.controller;

import java.io.IOException;
import lombok.extern.slf4j.Slf4j;
import org.dotroadsafety.service.CsvService;
import org.dotroadsafety.service.IndexingService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/dot-road-safety/index")
@Slf4j
public class IndexController {

  private final IndexingService indexingService;
  private final CsvService csvService;

  public IndexController(IndexingService indexingService,
      CsvService csvService) {
    this.indexingService = indexingService;
    this.csvService = csvService;
  }

  @GetMapping("/osm")
  public void indexOsm(@RequestParam(value = "pageSize", defaultValue = "500") Integer pageSize) {
    log.info("indexing OSM data...");
    indexingService.IndexAll(pageSize);
    log.info("indexing OSM data...done");
  }

  @GetMapping("/crashes")
  public void crashes(@RequestParam(value = "pageSize", defaultValue = "10000") Integer pageSize) throws IOException {
    log.info("indexing crashes data...");
    csvService.seedCrashesIndex(pageSize);
    log.info("indexing crashes data...done");
  }
}

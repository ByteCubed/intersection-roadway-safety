package org.dotroadsafety.controller;

import org.dotroadsafety.service.CsvService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/dot-road-safety/ingest")
public class IngestController {

  private final CsvService csvService;

  public IngestController(CsvService csvService) {
    this.csvService = csvService;
  }

  @GetMapping("/crashes")
  public void crashes(@RequestParam("filename") String filename) {
    csvService.csvImporter(filename);
  }

}

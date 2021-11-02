package org.dotroadsafety;

import org.dotroadsafety.service.CsvService;
import org.dotroadsafety.service.IndexingService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class DotRoadSafetyApplication implements CommandLineRunner {

    @Autowired
    private IndexingService indexingService;

    @Autowired
    private CsvService csvService;

    public static void main(String[] args) {
        SpringApplication.run(DotRoadSafetyApplication.class, args);
    }


    @Override
    public void run(String... args) throws Exception {
        //String fileName = "/Users/matthewleopin/Downloads/Crashes_in_DC.csv";
       // csvService.seedCrashesIndex(1000);
        //indexingService.seedSpatialIndex(500);
    }
}

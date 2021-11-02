package org.dotroadsafety.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.MappingIterator;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectReader;
import com.fasterxml.jackson.dataformat.csv.CsvMapper;
import com.fasterxml.jackson.dataformat.csv.CsvSchema;
import org.dotroadsafety.model.Crashes;
import org.dotroadsafety.model.Planet_osm_roads;
import org.dotroadsafety.repository.CrashesRepository;
import org.elasticsearch.action.admin.indices.delete.DeleteIndexRequest;
import org.elasticsearch.action.bulk.BulkRequest;
import org.elasticsearch.action.index.IndexRequest;
import org.elasticsearch.client.RequestOptions;
import org.elasticsearch.client.RestHighLevelClient;
import org.elasticsearch.client.indices.CreateIndexRequest;
import org.elasticsearch.client.indices.GetIndexRequest;
import org.elasticsearch.common.settings.Settings;
import org.elasticsearch.common.xcontent.XContentType;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.io.FileReader;
import java.io.IOException;
import java.io.Reader;
import java.lang.reflect.Field;
import java.net.UnknownHostException;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

@Service
public class CsvService {

    @Autowired
    CrashesRepository crashesRepository;

    @Autowired
    JdbcTemplate jdbcTemplate;

    @Autowired
    RestHighLevelClient restHighLevelClient;

    public void csvImporter(String fileName) {
        Instant start = Instant.now();
        Instant endTime = null;
        CsvMapper csvMapper = new CsvMapper();
        CsvSchema schema = CsvSchema.emptySchema().withHeader();

        ObjectReader objReader = csvMapper.readerFor(Crashes.class).with(schema);

        //connect to db
        //create table
        //insert data into table
        List<Crashes> crashesList = new ArrayList<>();

        try (Reader reader = new FileReader(fileName)) {
            MappingIterator<Crashes> mappingIterator = objReader.readValues(reader);

            jdbcTemplate.execute("DROP TABLE IF EXISTS crashes");
            boolean tableCreated = false;
            int total = 0;

            while (mappingIterator.hasNext()) {

                for (int i = 0; i < 10000; i++) {
                    Crashes crashes = mappingIterator.next();

                    if (!tableCreated) {
                        Object o = crashes;
                        StringBuilder sb = new StringBuilder("CREATE TABLE crashes (" +
                                "uid BIGSERIAL PRIMARY KEY,");
                        for (Field f : o.getClass().getDeclaredFields()) {
                            f.setAccessible(true);
                            if (f.getName().equalsIgnoreCase("uid")) {

                            } else if (f.getName().equalsIgnoreCase("offset")) {
                                sb.append(" \"offset\" " + reconcileType(f) + ",");
                            } else {
                                sb.append(" " + f.getName().toLowerCase() + " " + reconcileType(f) + ",");
                            }
                        }
                        sb.deleteCharAt(sb.length() - 1);
                        sb.append(")");
                        jdbcTemplate.execute(sb.toString());
                        tableCreated = true;
                    }


                    crashesList.add(crashes);
                    total++;
                    if (!mappingIterator.hasNext())
                        break;
                }

                crashesRepository.saveAll(crashesList);
                System.out.println("Saving ten thousand records. Current total: " + total);
                endTime = Instant.now();
                Duration timeElapsed = Duration.between(start, endTime);
                System.out.println("Time elapsed: " + timeElapsed.toMinutesPart() + "min, " + timeElapsed.toSecondsPart() + "sec");

            }

        } catch (IOException e) {
            e.printStackTrace();
        }

    }

    public void seedCrashesIndex(int pageSize) throws IOException {
        GetIndexRequest request = new GetIndexRequest("crashes");
        boolean exists = restHighLevelClient.indices().exists(request, RequestOptions.DEFAULT);

        if (exists) {
            DeleteIndexRequest deleteIndexRequest = new DeleteIndexRequest("crashes");

            try {
                restHighLevelClient.indices().delete(deleteIndexRequest, RequestOptions.DEFAULT);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        CreateIndexRequest createIndexRequest = new CreateIndexRequest("crashes");
        createIndexRequest.settings(
                Settings.builder().put("index.number_of_shards", 1)
                        .put("index.number_of_replicas", 0));
        try {
            restHighLevelClient.indices().create(createIndexRequest, RequestOptions.DEFAULT);

        } catch (IOException e) {
            e.printStackTrace();
        }

        Page<Crashes> crashes = null;
        int p = 0;
        do {
            crashes = crashesRepository.findAll(PageRequest.of(p, pageSize));

            Iterator<Crashes> iter = crashes.iterator();

            BulkRequest bulkRequest = new BulkRequest();

            while (iter.hasNext()) {
                Crashes crash = iter.next();
                ObjectMapper mapper = new ObjectMapper();
                String jsonString = mapper.writeValueAsString(crash);
                bulkRequest.add(new IndexRequest("crashes").id(String.valueOf(crash.getUid()))
                        .source(jsonString, XContentType.JSON));

                try {
                    restHighLevelClient.bulk(bulkRequest, RequestOptions.DEFAULT);
                } catch (IOException e) {
                    e.printStackTrace();
                }

            }

            if (crashes.hasNext())
                p++;
        } while (crashes.hasNext());
    }

    private String reconcileType(Field f) {
        String fieldType = null;

        switch (f.getType().getSimpleName().toLowerCase()) {
            case "double":
                fieldType = "NUMERIC";
                break;
            case "integer":
                fieldType = "INTEGER";
                break;
            case "long":
                fieldType = "BIGINT";
                break;
            default:
                fieldType = "VARCHAR(255)";
                break;
        }

        return fieldType;
    }

}

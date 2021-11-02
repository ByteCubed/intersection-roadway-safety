package org.dotroadsafety.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.dotroadsafety.model.*;
import org.dotroadsafety.repository.*;
import org.elasticsearch.action.admin.indices.delete.DeleteIndexRequest;
import org.elasticsearch.action.bulk.BulkRequest;
import org.elasticsearch.action.index.IndexRequest;
import org.elasticsearch.client.*;
import org.elasticsearch.client.indices.CreateIndexRequest;
import org.elasticsearch.client.indices.GetIndexRequest;
import org.elasticsearch.common.settings.Settings;
import org.elasticsearch.common.xcontent.XContentType;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.util.Iterator;

@Service
public class IndexingService {

    @Autowired
    private Planet_osm_roadsRepository planet_osm_roadsRepository;

    @Autowired
    Planet_osm_lineRepository planet_osm_lineRepository;

    @Autowired
    Planet_osm_pointRepository planet_osm_pointRepository;

    @Autowired
    Planet_osm_polygonRepository planet_osm_polygonRepository;

    @Autowired
    Spatial_ref_sysRepository spatial_ref_sysRepository;

    @Autowired
    RestHighLevelClient restHighLevelClient;

    public void seedRoadsIndex(int pageSize) throws IOException {
        GetIndexRequest request = new GetIndexRequest("roads");
        boolean exists = restHighLevelClient.indices().exists(request, RequestOptions.DEFAULT);

        if (exists) {
            DeleteIndexRequest deleteIndexRequest = new DeleteIndexRequest("roads");
            try {
                restHighLevelClient.indices().delete(deleteIndexRequest, RequestOptions.DEFAULT);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        CreateIndexRequest createIndexRequest = new CreateIndexRequest("roads");
        createIndexRequest.settings(
                Settings.builder().put("index.number_of_shards", 1)
                        .put("index.number_of_replicas", 0));
        try {
            restHighLevelClient.indices().create(createIndexRequest, RequestOptions.DEFAULT);

        } catch (IOException e) {
            e.printStackTrace();
        }

        Page<Planet_osm_roads> roads = null;
        int p = 0;
        do {
            roads = planet_osm_roadsRepository.findAll(PageRequest.of(p, pageSize));

            Iterator<Planet_osm_roads> iter = roads.iterator();

            BulkRequest bulkRequest = new BulkRequest();

            while (iter.hasNext()) {
                Planet_osm_roads road = iter.next();
                ObjectMapper mapper = new ObjectMapper();
                String jsonString = mapper.writeValueAsString(road);
                bulkRequest.add(new IndexRequest("roads").id(String.valueOf(road.getOsm_id()))
                        .source(jsonString, XContentType.JSON));

                try {
                    restHighLevelClient.bulk(bulkRequest, RequestOptions.DEFAULT);
                } catch (IOException e) {
                    e.printStackTrace();
                }

            }

            if (roads.hasNext())
                p++;
        } while (roads.hasNext());
    }

    public void seedPolygonsIndex(int pageSize) throws IOException {
        GetIndexRequest request = new GetIndexRequest("polygons");
        boolean exists = restHighLevelClient.indices().exists(request, RequestOptions.DEFAULT);

        if (exists) {
            DeleteIndexRequest deleteIndexRequest = new DeleteIndexRequest("polygons");
            try {
                restHighLevelClient.indices().delete(deleteIndexRequest, RequestOptions.DEFAULT);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        CreateIndexRequest createIndexRequest = new CreateIndexRequest("polygons");
        createIndexRequest.settings(
                Settings.builder().put("index.number_of_shards", 1)
                        .put("index.number_of_replicas", 0));
        try {
            restHighLevelClient.indices().create(createIndexRequest, RequestOptions.DEFAULT);

        } catch (IOException e) {
            e.printStackTrace();
        }

        Page<Planet_osm_polygon> polygons = null;
        int p = 0;
        do {
            polygons = planet_osm_polygonRepository.findAll(PageRequest.of(p, pageSize));
            Iterator<Planet_osm_polygon> iter = polygons.iterator();

            BulkRequest bulkRequest = new BulkRequest();

            while (iter.hasNext()) {
                Planet_osm_polygon polygon = iter.next();
                ObjectMapper mapper = new ObjectMapper();
                String jsonString = mapper.writeValueAsString(polygon);
                bulkRequest.add(new IndexRequest("polygons").id(String.valueOf(polygon.getOsm_id()))
                        .source(jsonString, XContentType.JSON));

                try {
                    restHighLevelClient.bulk(bulkRequest, RequestOptions.DEFAULT);
                } catch (IOException e) {
                    e.printStackTrace();
                }

            }
            if (polygons.hasNext())
                p++;
        } while (polygons.hasNext());
    }

    public void seedSpatialIndex(int pageSize) throws IOException {
        GetIndexRequest request = new GetIndexRequest("spatialref");
        boolean exists = restHighLevelClient.indices().exists(request, RequestOptions.DEFAULT);

        if (exists) {
            DeleteIndexRequest deleteIndexRequest = new DeleteIndexRequest("spatialref");
            try {
                restHighLevelClient.indices().delete(deleteIndexRequest, RequestOptions.DEFAULT);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        CreateIndexRequest createIndexRequest = new CreateIndexRequest("spatialref");
        createIndexRequest.settings(
                Settings.builder().put("index.number_of_shards", 1)
                        .put("index.number_of_replicas", 0));
        try {
            restHighLevelClient.indices().create(createIndexRequest, RequestOptions.DEFAULT);

        } catch (IOException e) {
            e.printStackTrace();
        }
        Page<Spatial_ref_sys> spatialRefSys = null;
        int p = 0;
        do {
            spatialRefSys = spatial_ref_sysRepository.findAll(PageRequest.of(p, pageSize));
            Iterator<Spatial_ref_sys> iter = spatialRefSys.iterator();

            BulkRequest bulkRequest = new BulkRequest();

            while (iter.hasNext()) {
                Spatial_ref_sys spatials = iter.next();
                ObjectMapper mapper = new ObjectMapper();
                String jsonString = mapper.writeValueAsString(spatialRefSys);
                bulkRequest.add(new IndexRequest("spatialref").id(String.valueOf(spatials.getSrid()))
                        .source(jsonString, XContentType.JSON));

                try {
                    restHighLevelClient.bulk(bulkRequest, RequestOptions.DEFAULT);
                } catch (IOException e) {
                    e.printStackTrace();
                }

            }
            if (spatialRefSys.hasNext())
                p++;
        } while (spatialRefSys.hasNext());
    }

    public void seedPointsIndex(int pageSize) throws IOException {
        GetIndexRequest request = new GetIndexRequest("points");
        boolean exists = restHighLevelClient.indices().exists(request, RequestOptions.DEFAULT);

        if (exists) {
            DeleteIndexRequest deleteIndexRequest = new DeleteIndexRequest("points");
            try {
                restHighLevelClient.indices().delete(deleteIndexRequest, RequestOptions.DEFAULT);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        CreateIndexRequest createIndexRequest = new CreateIndexRequest("points");
        createIndexRequest.settings(
                Settings.builder().put("index.number_of_shards", 1)
                        .put("index.number_of_replicas", 0));
        try {
            restHighLevelClient.indices().create(createIndexRequest, RequestOptions.DEFAULT);

        } catch (IOException e) {
            e.printStackTrace();
        }
        Page<Planet_osm_point> points = null;
        int p = 0;
        do {
            points = planet_osm_pointRepository.findAll(PageRequest.of(p, pageSize));
            Iterator<Planet_osm_point> iter = points.iterator();


            BulkRequest bulkRequest = new BulkRequest();

            while (iter.hasNext()) {
                Planet_osm_point point = iter.next();
                ObjectMapper mapper = new ObjectMapper();
                String jsonString = mapper.writeValueAsString(point);
                bulkRequest.add(new IndexRequest("points").id(String.valueOf(point.getOsm_id()))
                        .source(jsonString, XContentType.JSON));

                try {
                    restHighLevelClient.bulk(bulkRequest, RequestOptions.DEFAULT);
                } catch (IOException e) {
                    e.printStackTrace();
                }

            }
            if (points.hasNext())
                p++;
        } while (points.hasNext());
    }

    public void seedLinesIndex(int pageSize) throws IOException {
        GetIndexRequest request = new GetIndexRequest("lines");
        boolean exists = restHighLevelClient.indices().exists(request, RequestOptions.DEFAULT);

        if (exists) {
            DeleteIndexRequest deleteIndexRequest = new DeleteIndexRequest("lines");
            try {
                restHighLevelClient.indices().delete(deleteIndexRequest, RequestOptions.DEFAULT);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        CreateIndexRequest createIndexRequest = new CreateIndexRequest("lines");
        createIndexRequest.settings(
                Settings.builder().put("index.number_of_shards", 1)
                        .put("index.number_of_replicas", 0));
        try {
            restHighLevelClient.indices().create(createIndexRequest, RequestOptions.DEFAULT);

        } catch (IOException e) {
            e.printStackTrace();
        }
        Page<Planet_osm_line> lines = null;
        int p = 0;
        do {
            lines = planet_osm_lineRepository.findAll(PageRequest.of(p, pageSize));
            Iterator<Planet_osm_line> iter = lines.iterator();

            BulkRequest bulkRequest = new BulkRequest();

            while (iter.hasNext()) {
                Planet_osm_line line = iter.next();
                ObjectMapper mapper = new ObjectMapper();
                String jsonString = mapper.writeValueAsString(line);
                bulkRequest.add(new IndexRequest("lines").id(String.valueOf(line.getOsm_id()))
                        .source(jsonString, XContentType.JSON));

                try {
                    restHighLevelClient.bulk(bulkRequest, RequestOptions.DEFAULT);
                } catch (IOException e) {
                    e.printStackTrace();
                }

            }
            if (lines.hasNext())
                p++;
        } while (lines.hasNext() && p < 10);
    }

    public void IndexAll(int pageSize) {

        try {
            seedRoadsIndex(pageSize);
        } catch (IOException e) {
            e.printStackTrace();
        }

        try {
            seedLinesIndex(pageSize);
        } catch (IOException e) {
            e.printStackTrace();
        }

        try {
            seedPointsIndex(pageSize);
        } catch (IOException e) {
            e.printStackTrace();
        }

        try {
            seedPolygonsIndex(pageSize);
        } catch (IOException e) {
            e.printStackTrace();
        }
        try {
            seedSpatialIndex(pageSize);
        } catch (IOException e) {
            e.printStackTrace();
        }
//        } catch (JsonProcessingException e) {
//            e.printStackTrace();
//        } catch (UnknownHostException e) {
//            e.printStackTrace();
//        }
    }

}



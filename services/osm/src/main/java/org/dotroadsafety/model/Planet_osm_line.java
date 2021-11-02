package org.dotroadsafety.model;


import lombok.Builder;
import lombok.Data;
import org.springframework.data.annotation.Id;

@Data
@Builder
public class Planet_osm_line {
    @Id
    private long osm_id;
    private String boundary;
    private String name;
    private String highway;
    private String ref;
    private String surface;
    private String z_order;
    //private String way;

}

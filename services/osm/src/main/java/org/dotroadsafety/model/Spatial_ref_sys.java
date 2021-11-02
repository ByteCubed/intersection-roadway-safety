package org.dotroadsafety.model;


import lombok.Builder;
import lombok.Data;
import org.springframework.data.annotation.Id;

@Data
@Builder
public class Spatial_ref_sys {
    @Id
    private long srid;
    private String auth_name;
    private String auth_srid;
    private String srtext;

}

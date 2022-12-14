create materialized view if not exists curated_way_feature_view as
    select  ni.node_id,
    		wfv.way_id,
            wfv."name",
            wfv.tiger_name_direction_prefix,
            wfv.tiger_name_direction_prefix_1,
            wfv.tiger_name_base,
            wfv.tiger_name_base_1,
            wfv.tiger_name_base_2,
            wfv.tiger_name_direction_suffix,
            wfv.tiger_name_direction_suffix_1,
            wfv.tiger_name_type_1,
            wfv.tiger_name_type_2,
            wfv.hfcs, -- highway functional classification system
            wfv.old_name,
            wfv."ref",
            wfv.footway,
            wfv.highway,
            wfv.railway,
            wfv.sidewalk,
            wfv.oneway,
            wfv.traffic_sign,
            wfv.tunnel_name,
            wfv.maxheight,
            wfv.min_height,
            wfv.lanes, -- number seems wild and inaccurate
            wfv.lanes_forward,
            wfv.lanes_backward,
            wfv.lanes_both_ways,
            wfv.route,
            wfv.lit,
            wfv.surface,
            wfv.turn_lanes,
            wfv."access",
            wfv.boundary,
            wfv.junction,
            wfv.road_marking,
            wfv.frequency,
            wfv."usage",
            wfv.dcgis_adj_school,
            wfv.dcgis_zone_,
            wfv.tunnel,
            wfv.maxspeed,
            wfv.maxspeed_type,
            wfv.maxspeed_conditional,
            wfv.crossing,
            wfv.bicycle,
            wfv.cycleway,
            wfv.foot,
            wfv.nhs, -- national highway system
            wfv.dataset,
            wfv."source",
            wfv.building
    from node_intersections ni
    join way_node wn on ni.node_id = wn.node_id
    join way_feature_view wfv on wn.way_id = wfv.way_id;

CREATE INDEX if not exists curated_way_feature_view_index ON curated_way_feature_view(way_id);
create index if not exists cwfv_node_index on curated_way_feature_view(node_id);

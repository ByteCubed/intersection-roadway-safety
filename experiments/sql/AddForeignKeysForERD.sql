-- Add foreign keys for ERD creation
show search_path;
set search_path to dc,public;

alter table way_node add constraint way_node_to_way_fk foreign key (way_id) references way (way_id);
alter table way_feature add constraint way_feature_to_way_fk foreign key (way_id) references way (way_id);
alter table waylet add constraint waylet_to_way_fk foreign key (way_id) references way (way_id);

alter table way_node add constraint way_node_to_node_fk foreign key (node_id) references node (node_id);
alter table waylet add constraint waylet_to_node1_fk foreign key (node_id1) references node (node_id);
alter table waylet add constraint waylet_to_node2_fk foreign key (node_id2) references node (node_id);
alter table intersection_angle add constraint angle_to_node_fk foreign key (node_id) references node (node_id);
alter view curated_way_feature_view add constraint cwfv_to_node_fk foreign key (node_id) references node (node_id);

alter table intersection_angle add constraint angle_to_node_int_fk foreign key (node_id) references node_intersections (node_id);
alter table intersection_angle add constraint angle_to_node_feat_fk foreign key (node_id) references intersection_features (node_id);

alter table intersection_angle add constraint angle_to_waylet1_fk foreign key (waylet_id1) references waylet (waylet_id);
alter table intersection_angle add constraint angle_to_waylet2_fk foreign key (waylet_id2) references waylet (waylet_id);

alter table intersection_features add constraint intersection_features_to_node_intersections foreign key (node_id) references node_intersections (node_id);
alter table intersection_features add constraint intersection_features_to_node foreign key (node_id) references node (node_id);
alter table node_intersections add constraint node_intersections_to_node foreign key (node_id) references node (node_id);


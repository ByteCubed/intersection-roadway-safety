psql -h $HOSTNAME -U $POSTGRES_USER -d $POSTGRES_DB -f /postprocess/node_creation_query.sql << EOF
$POSTGRES_PASSWORD
EOF
psql -h $HOSTNAME -U $POSTGRES_USER -d $POSTGRES_DB -f /postprocess/way_node_creation_query.sql << EOF
$POSTGRES_PASSWORD
EOF
psql -h $HOSTNAME -U $POSTGRES_USER -d $POSTGRES_DB -f /postprocess/way_feature_creation_query.sql << EOF
$POSTGRES_PASSWORD
EOF
psql -h $HOSTNAME -U $POSTGRES_USER -d $POSTGRES_DB -f /postprocess/create_way_feature_view.sql << EOF
$POSTGRES_PASSWORD
EOF
psql -h $HOSTNAME -U $POSTGRES_USER -d $POSTGRES_DB -f /postprocess/way_creation_query.sql << EOF
$POSTGRES_PASSWORD
EOF
psql -h $HOSTNAME -U $POSTGRES_USER -d $POSTGRES_DB -f /postprocess/populate_node_road_status.sql << EOF
$POSTGRES_PASSWORD
EOF
psql -h $HOSTNAME -U $POSTGRES_USER -d $POSTGRES_DB -f /postprocess/waylet_creation_query.sql << EOF
$POSTGRES_PASSWORD
EOF
psql -h $HOSTNAME -U $POSTGRES_USER -d $POSTGRES_DB -f /postprocess/node_intersection_creation_query.sql << EOF
$POSTGRES_PASSWORD
EOF
psql -h $HOSTNAME -U $POSTGRES_USER -d $POSTGRES_DB -f /postprocess/traffic_volume_creation_query.sql << EOF
$POSTGRES_PASSWORD
EOF
psql -h $HOSTNAME -U $POSTGRES_USER -d $POSTGRES_DB -f /postprocess/create_curated_way_feature_view.sql << EOF
$POSTGRES_PASSWORD
EOF
psql -h $HOSTNAME -U $POSTGRES_USER -d $POSTGRES_DB -f /postprocess/link_crashes_to_intersections.sql << EOF
$POSTGRES_PASSWORD
EOF
psql -h $HOSTNAME -U $POSTGRES_USER -d $POSTGRES_DB -f /postprocess/intersection_angle_creation_query.sql << EOF
$POSTGRES_PASSWORD
EOF
psql -h $HOSTNAME -U $POSTGRES_USER -d $POSTGRES_DB -f /postprocess/intersection_feature_creation_query.sql << EOF
$POSTGRES_PASSWORD
EOF


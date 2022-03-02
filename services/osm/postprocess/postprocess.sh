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

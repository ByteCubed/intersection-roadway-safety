psql -h $HOSTNAME -U $POSTGRES_USER -d $POSTGRES_DB -f /intersections/intersection_creation_query.sql << EOF
$POSTGRES_PASSWORD
EOF
FROM alpine:3.14

ENV OSM2PGSQL_VERSION 1.5.1

RUN apk --update-cache add \
  cmake \
  make \
  g++ \
  boost-dev \
  expat-dev \
  bzip2-dev \
  zlib-dev \
  libpq \
  proj-dev \
  lua5.3-dev \
  postgresql-dev \
  git

WORKDIR /usr/src

RUN git clone --depth 1 --branch ${OSM2PGSQL_VERSION} https://github.com/openstreetmap/osm2pgsql.git \
  && mkdir -p osm2pgsql/build \
  && cd osm2pgsql/build \
  && cmake .. \
  && make

WORKDIR /usr/src/osm2pgsql/build
RUN ls -la
RUN cat Makefile

RUN cd /usr/src/osm2pgsql/build \
  && make install

ENTRYPOINT [ "/usr/local/bin/osm2pgsql" ]

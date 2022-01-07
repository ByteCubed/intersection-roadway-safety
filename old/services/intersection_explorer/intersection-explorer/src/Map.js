import React, {useRef, useCallback, useState} from 'react';
import DeckGL from '@deck.gl/react';
import ReactMapGL from 'react-map-gl';
import {MapboxLayer} from '@deck.gl/mapbox';

import {MVTLayer} from '@deck.gl/geo-layers';
import {Component} from 'react';
import {HeatmapLayer} from '@deck.gl/aggregation-layers';
import {GeoJsonLayer} from '@deck.gl/layers';
import {TileLayer} from '@deck.gl/geo-layers';
import style from './basic_preview.json';
import {MapView} from '@deck.gl/core';

import {PathStyleExtension} from '@deck.gl/extensions';
import INCIDENTS from './dcincidents.json';
import {_MapContext as MapContext, NavigationControl} from 'react-map-gl';
import MAPSTYLE from './basic_preview.json';
import INTERSECTIONS from './dc_intersections.json';
import { GeoJSONSource } from 'mapbox-gl';


export default function Map() {  
  const [viewport, setViewport] = useState({    
    latitude: 38.9072,
    longitude: -77.0369,
    zoom: 11
  });
  const DEFAULT_COLOR = [232, 229, 216];

      // https://deck.gl/docs/api-reference/mapbox/overview
      const view = new MapView({
        id: 'mapview',
        width: '100%'
      })
  
      const layer = new GeoJsonLayer({
        id: 'incidents',
        data: INCIDENTS,
        pickable: true,
        filled: true,
        stroked: true,
        getLineColor: [50, 110, 250, 100],
        getLineWidth: 1,
        getFillColor: [117, 157, 270, 20],
        pointRadiusUnits: 'pixels',
        getRadius: 3,
        onClick: (info, event) => console.log('Clicked:', info, event),
        visible: false
      });
  
      const intersection_layer = new GeoJsonLayer({
        id: 'intersections',
        data: INTERSECTIONS,
        pickable: true,
        filled: true,
        stroked: false,
        getLineColor: [50, 110, 250, 100],
        getLineWidth: 1,
        getFillColor: [117, 157, 270],
        pointRadiusUnits: 'meters',
        getRadius: 5,
        visible: true,
      })
  
      const heatlayer = new HeatmapLayer({
        id: 'heatmap',
        data: INCIDENTS.features,
        getPosition: d => d.geometry.coordinates,
        getWeight: 1,
        opacity: 0.7,
        radiusPixels: 25,
        visible: true
      })
  
      const [glContext, setGLContext] = useState();
      const deckRef = useRef(null);
      const mapRef = useRef(null);
  
      const onMapLoad = useCallback(() => {
        const map = mapRef.current.getMap();
        const deck = deckRef.current.deck;
    
        // You must initialize an empty deck.gl layer to prevent flashing
        map.addLayer(
          // This id has to match the id of the deck.gl layer
          new MapboxLayer({ id: "incidents", deck }),
          // Optionally define id from Mapbox layer stack under which to add deck layer
          'beforeId'
        );
      }, []);
      
      return (
        <DeckGL
          ref={deckRef}
          layers={[intersection_layer, layer, heatlayer]}
          initialViewState={viewport}
          controller={true}
          onWebGLInitialized={setGLContext}
          views={[view]}
          getTooltip={({object}) => object && {
            text: object.properties.tooltip
          }}
          glOptions={{
            stencil: true
          }}
        >
          {glContext && <ReactMapGL
        width="100vw"
        height="100vh"
        mapboxApiUrl="http://localhost:8080/us_dc"
        mapStyle={MAPSTYLE}
        {...viewport}
        onViewportChange={nextViewport => setViewport(nextViewport)}
        ></ReactMapGL>
          }
        </DeckGL>
      );
    }  

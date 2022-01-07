Roadway Segment
===============

Many of the roadway segment attributes can be derived directly from OSM tags.
This section decribes a small collection of the possible elements.

.. contents:: **Contents:**
    :depth: 2
    :local:

1-2: County Name & County Code
------------------------------

The County Code is defined by the Federal Information Processing Standard (FIPS) code or
equivalent entity where the segment is located.

The FIPS code is defined by `census.gov annually <https://www.census.gov/geographies/reference-files/2019/demo/popest/2019-fips.html>`_.

We can use the FIPS data to create an automatically validated datatype to represent county names and FIPS codes.



8-9: Route Number & Route/Street Name
-------------------------------------

OSM labels roadway segments with names and, where applicable, route numbers. We already pull this information 
into our model.

.. note::

    OSM initially imported TIGER (Topologically Integrated Geographic Encoding and Referencing system) data.
    See `this note <https://wiki.openstreetmap.org/wiki/TIGER>`_ for important information about the import.
    It is unlikely that the data will be imported again. There are some legacy `tiger` tags in OSM data, 
    and some efforts have been done to convert them into more consistent OSM tags, but it is not complete.

13: Segment Length
------------------

OSM labels edges with length. However, we must still investigate the definition of roadway "segment" in
the MIRE v2.0 standard relative to OSM's roadway segments.

.. note:: **Key Question**

    How is a roadway "segment" defined? How is a roadway broken into segments?


32: Number of Through Lanes
---------------------------

Once more, OSM data labels roadways with the number of lanes. 




    

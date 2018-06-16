## Tree Range Visualization

Before hiking a section of the Appalachian Trail, I found myself wondering: which of the trees in a particular area are most unique/distinctive?

After a wonderful journey through dendrology, shapefiles, and choropleths, the result:

![tree range visualization](https://github.com/nsrivast/tree-range-viz/blob/master/tree.png)

The goal of this project was to create a data visualization to explore and examine the distribution of tree species across the US.

Launch the [visualization](http://nsrivast.github.io/tree-range-viz/), or read [an exploration of the results](http://nsrivast.github.io/tree-range-viz/analysis.html). The rest of this README explains how I built the visualization, the data formats and libraries I used (shapefiles, geoJSON, Shapely for Python, Leaflet), and the analysis and design choices I made along the way. 

### Outline

1. [Initial Research](#initial)

2. [Data Acquisition and Parsing](#data)

3. [Intersection Calculations](#intersection)

4. [Explore Results](#explore)

5. [Build Visualization](#build)
	
### <a name="initial"></a>Initial Research

Looking for resources on the ranges of tree species led me quickly to the tree range maps of [Elbert Little](http://en.wikipedia.org/wiki/Elbert_Luther_Little), a botanist who (in his tenure as the amazingly-titled "Chief Dendrologist" of the USDA Forest Service) aggregated data from various field studies to produce a set of tree range maps for 678 tree species of North America. These maps were digitized by the USGS and are available [here](http://esp.cr.usgs.gov/data/little/) in PDF and shapefile format. [Here's](https://github.com/nsrivast/tree-range-viz/blob/master/data/tree_ranges/abiebals/abiebals.pdf) an example of a range map for the balsam fir.

##### Format and structure of tree data
Little's tree ranges are represented by shapefiles, a common format in the well-developed field of [Geographic Information Systems (GIS)](http://en.wikipedia.org/wiki/Geographic_information_system). After downloading and examining the shapefiles, and after some research and deliberation, I decided to convert the shapefiles to the GeoJSON format, for a few reasons: 

* it is a lighter format, and I only needed the basic outlines of the tree ranges
* it is a JSON format, easily used in Javascript and the most popular mapping libraries
* it is easier to parse as a human reader

For the conversion I used [ogr2ogr](http://www.gdal.org/ogr2ogr.html), an open-source library for processing geospatial data. There are various conversion details related to the projection between different [coordinate systems](http://maps.unomaha.edu/Peterson/gis/notes/MapProjCoord.html) - [this article](http://ben.balter.com/2013/06/26/how-to-convert-shapefiles-to-geojson-for-use-on-github/) was useful in guiding me through the process.

The converted GeoJSON files looked like this, excluding some extraneous fields:

```
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "AREA" : 425.2352,
        "PERIMETER" : 9474.2483,
        "CODE" : 1,
      },
      "geometry" : {
        "type" : "Polygon",
        "coordinates" : [ [ [-121.61, 36.21], [-121.83, 36.83], ... ] ]
      }
    },
    ...
  ]
}
```

Each tree range was represented by a list of features (map regions), each of which had properties including area, perimeter, and code, and each of whose geometry was a Polygon with a list of (longitude, latitude) coordinate pairs describing its outline. Note that the coordinates are actually a **list of list** of coordinate pairs - this is because sometimes the feature is of type MultiPolygon rather than Polygon, and multiple polygons are described.

Github has a convenient built-in GeoJSON renderer, so you can see the [balsam fir tree's range](/data/tree_ranges/abiebals/abiebals.geojson) and compare with [the same data in GeoJSON format](https://raw.githubusercontent.com/nsrivast/tree-range-viz/master/data/tree_ranges/abiebals/abiebals.geojson).

##### Format and structure of location data
The US Census Bureau maintains boundary files for various geographic areas of the country and at various resolution levels. I wanted a range of area sizes - [states](https://www.census.gov/geo/maps-data/data/cbf/cbf_state.html), [counties](https://www.census.gov/geo/maps-data/data/cbf/cbf_counties.html), and towns. I couldn't locate a national data source for townships, but [this article](http://techslides.com/mapping-town-boundaries-with-d3) led me to township data for various Northeast states.

After converting to GeoJSON, the data looked similar to the tree range data except with several additional fields such as county or state name or postal code. I took an appropriate combination of these additional fields to get a unique name for each location.

##### Plan out rest of project and code architecture
I now had enough information to plan out the rest of the project. After downloading and converting the tree range and geographic location data to GeoJSON, I would intersect the two data sets, either through some polygon intersection calculation or a suitable simplification. The results of the intersection would list which tree species were present at which locations, and which locations were spanned by each species. Next, I would explore the data to identify which metrics were most informative in showing the tree distributions. Finally, I would design the visualization to show these metrics and actually build it.

### <a name="data"></a>Data Acquisition and Parsing
This step involved downloading all 678 tree range shapefiles and the thousands of location shapefiles, converting them to GeoJSON format, and checking a few visually to make sure the converted GeoJSON regions were sensible. 

I included in this repository the converted location GeoJSON files for states and counties, and for towns in 7 northeast states. I also included the raw data for only the first 10 tree species alphabetically due to file size. All of these can be found in the [data folder](/data).

### <a name="intersection"></a>Intersection Calculations

##### Research, think on how to perform range calculation
For every tree and location, I was interested in the answer to the question: does the tree region (a set of non-overlapping polygons) cover or in some way intersect the location region (a different set of polygons)? My first thought was to run an exhaustive polygon intersection algorithm, but the resolution of the tree range data set (roughly 1MB each) and some research on algorithms prompted me to look for a simplification.

My next thought was to simplify one region to one point or a set of points and calculate whether those points were located within the other region's polygons. There appeared to be a [literature](http://en.wikipedia.org/wiki/Point_in_polygon) on the subject and some implementations that fit my requirements. Because geographic locations were more regularly shaped than tree ranges, I decided to calculate the centroid of each region and calculate whether the centroid existed in at least one polygon for a given tree range. I kept in mind that my results would be less accurate for larger regions (such as states) because I was only sampling the center of the region.

##### Select, install, test library for PolygonContainsPoint and PolygonCenter calculations
Most of the fastest implementations used customized databases that handled GIS data or were written in C/C++, but these [two](http://www.mhermans.net/geojson-shapely-geocoding.html) [articles](http://stackoverflow.com/questions/20776205/point-in-polygon-with-geojson-in-python) led me to the Shapely library for Python. I tested the algorithm with a test tree range and some sample points and it seemed to work correctly. It was also reasonably fast, capable of processing all of the polygons for a tree range in less than a second on my 2.8GHz MacBook Pro..

##### Write code for intersection calculations, run for all data
I wrote code to load and calculate the centroid of geographic locations, to calculate intersections between the centroids and tree range regions, and to store the results. For the entire set of northeast townships, the largest data set, the calculations took about 2.5 hours.

The important code is located in the [scripts folder](/scripts/) and contains the following files:

| Filename | Description |
|:---------|-------------|
| [locations.py](/scripts/locations.py) | loads, parses geoJSON files representing geographic areas (states, counties, townships) |
| [treeranges.py](/scripts/treeranges.py) | loads, parses geoJSON files representing ranges of trees |
| [intersections.py](/scripts/intersections.py) | calculates intersections between tree ranges and geographic areas |
| [stats.py](/scripts/stats.py) | calculates statistics on intersection data, such as coverage fractions |
| [map_settings.py](/scripts/map_settings.py) | default map parameters for various visualizations |
| [geojson.py](/scripts/geojson.py) | methods for preparing and writing .geojson files (and associated .js files) |

### <a name="explore"></a>Explore Results

##### Examine data and think on visualization metrics
For the 678 tree species, 50 states, ~3000 counties, and ~3500 northeast towns, I had a list of all tree species contained in each region and all regions covered by each species. The next step was to consider how to best represent and visualize the information.

Starting from the tree data, it would be somewhat interesting to see how many regions and what total area each tree covered, although this information was already given directly in the tree range maps. I couldn't think of many fruitful comparisons to be made between trees besides size of coverage area, since metrics like shape, directionality, or region of coverage were probably better examined per-location than per-tree. For interest, here are the trees with largest and smallest reported ranges:

Rank | Largest Range | Smallest Range
:---:|:--------|:---------
1 | common juniper (_Juniperus communis_) | black calabash (_Amphitecna latifolia_)
2 | quaking aspen (_Populus tremuloides_) | Florida cupania (_Cupania glabra_)
3 | black spruce (_Picea mariana_) | rough strongbark (_Bourreria radula_)
4 | white spruce (_Picea glauca_) | balsam torchwood (_Amyris balsamifera_)
5 | paper birch (_Betula papyrifera_) | long spine acacia (_Acacia macracantha_)
6 | red osier dogwood (_Cornus stolonifera_) | bitterbush (_Picramnia pentandra_)
7 | Bebb willow (_Salix bebbiana_) | buccaneer palm (_Pseudophoenix sargentii_)
8 | balsam poplar (_Populus balsamifera_) | cinnecord (_Acacia choriophylla_)
9 | tamarack (_Larix laricina_) | West Indies satinwood (_Zanthoxylum flavum_)
10 | coyote willow (_Salix exigua_) | Florida clusia (_Clusia rosea_)

More interesting was to start from the location data, which could show metrics as layers on top of the geographical data. I also thought some measure of how unique the location's species were might be interesting, especially relative to nearby regions. Could we correlate the country's geophysical regions and boundaries to features of the tree range data?

Lastly, for a more in-depth look at the universe of tree types, I could overlay additional data such as broader taxonomic classifications or specific features - e.g. deciduous versus evergreen. This would require additional data sources, such as scraping some public tree [database](http://www.fs.fed.us/database/feis/plants/tree/).

I decided to play around with some basic visualizations to explore the data and decide what metrics might be most useful to display.

### <a name="build"></a>Build Visualization

##### Find map library for interactive visualization
There are [lots](http://gis.stackexchange.com/questions/8032/how-do-various-javascript-mapping-libraries-compare) of mapping libraries out there. Because I wanted to avoid a commercial API and needed something relatively simple, I choose Leaflet which had some [examples](http://leafletjs.com/examples/choropleth) that seemed to be similar to my intended result. 

##### Build basic visualization, experiment with various metrics
I calculated various metrics of interest in each region (number of trees, distribution of trees, uniqueness of trees) and started looking at different regions of the country with states and counties colored by each metric. It was immediately clear that state-level location data was too coarse for informative results; California, for example, registered very few tree species only because its centroid was in the arboreally-sparse Central Valley. County-level data was more interesting, although looking at the full country was overwhelming. I focused on counties in different regions, such as the northeast states whose geography I had a better intuition for.

The most interesting metric I created tried to measure how unique each county's tree population was. I calculated a "coverage" metric for each tree species defined as the fraction of total locations in the sample for which the tree was present. Then, I calculated the "average coverage" for each location across all the trees it contained. In other words:

For a given tree species:
> coverage = (# of regions covered by the tree range) / (# of total regions)

For a given region:
> average coverage = mean coverage of all trees contained by the region

This gave interesting results, in which I could see the geographical uniqueness of the Adirondack and Acadian regions and the southern coastal regions of Connecticut and New York City. However, results were skewed for regions with fewer trees, such as Nevada whose two tree species were relatively rare and gave the state a strong uniqueness score.

I wanted to see my average coverage somewhow normalized by number of tree species, so I assigned each map region a hue (color) based on its average coverage and a saturation (lightness/darkness) based on its number of species. The [resulting visualization](http://nsrivast.github.io/tree-range-viz/) produced the set of graphics described in [this analysis](http://nsrivast.github.io/tree-range-viz/analysis.html).

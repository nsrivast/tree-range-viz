## Tree Range Visualization

### Summary
The goal of this project was to create a data exploration tool to examine the distribution of tree species across North America. I wanted an easy way to identify which trees are prevalent in different locations and geographies of the continent, without having to search through Wikipedia:Flora pages for nearby parks or cities. I also wanted to understand the range of various tree species and tree types.

### Background
In preparation for a series of section hikes of the Appalachian Trail, I wanted to familiarize myself with the most common tree species I would encounter. I found online resources on plants common to specific regions, such as local parks and forests, but no central resource that answered the question: which trees are prevalent in a given area of the country?

### Result
The final visualization is located [here]. The rest of this README explains how I built the tool, the analysis and design decisions I made along the way, and a basic introduction to data formats and libraries I used (shapefiles, geoJSON, Shapely for Python, Leaflet).


### Outline

1. [Initial Research] (#initial) 3hr
  1. [Inspiration for problem, initial research, tree range data acquisition] (#initial-inspiration)
  2. [Explore format and structure of tree range data] (#initial-explore)
  3. [Explore format and structure of location data] (#initial-explore2)
  4. [Plan out rest of project and code architecture] (#initial-plan)

2. [Data Acquisition and Parsing] (#data) 2hr

3. [Side Project: Ranking Trees by Range Size] (#side) 1hr
  1. [Examine AREA field] (#side-examine) 
  2. [Aggregate and rank species by area. Check, explore results] (#side-aggregate)
	
4. [Intersection Calculations] (#intersection) 4hr
  1. [Research, think on how to perform range calculation] (#intersection-research)
  2. [Select, install, test library for PolygonContainsPoint and PolygonCenter calculations] (#intersection-select)
	3. [Build library to calculate centroid for locations and intersection between tree ranges and locations, run for all data] (#intersection-build)

5. [Explore Results] (#explore) 2hr
  1. [Produce summary statistics] (#explore-produce)
	2. [Look for patterns and think on visualization metrics] (#explore-look)

6. [Build Visualization] (#build) 6hr
  1. [Find map library for interactive visualization] (#build-find)
  2. [Build basic visualization] (#build-build)
	3. [Show tree ranges on map] (#build-show) 
  4. [Experiment with displaying various metrics] (#build-experiment)
	
7. [Final Improvements and Deployment] (#final) 4hr
  1. [Finalize visualization and host] (#final-finalize)
	2. [Write this README] (#final-write)


### <a name="initial"></a>Initial Research

#### <a name="initial-inspiration"></a>Inspiration for problem, initial research, data source acquisition
Looking for resources on the ranges of tree species led me quickly to the tree range maps of [Elbert Little] (http://en.wikipedia.org/wiki/Elbert_Luther_Little), a botanist who (in his tenure as the amazingly-titled "Chief Dendrologist" of the USDA Forest Service) aggregated data from various sources to produce a set of tree range maps for 678 tree species of North America. These maps were digitized by the USGS and are available [here] (http://esp.cr.usgs.gov/data/little/) in PDF and shapefile format. An example of a range map for the balsam fir:

![Range map for balsam fir ](http://esp.cr.usgs.gov/data/little/abiebals.pdf "Range map for balsam fir")

#### <a name="initial-explore"></a>Explore format and structure of data source
Little's tree ranges are represented by shapefiles, a common format for information in the well-developed field of [Geographic Information Systems (GIS)] (http://en.wikipedia.org/wiki/Geographic_information_system). After downloading and examining the shapefiles, and after some research and deliberation, I decided to convert the shapefiles to the GeoJSON format, for a few reasons: 

* it is a lighter format, and I only needed the basic outlines of the tree ranges
* it is easier to parse as a human reader
* it is in JSON, which of course is easily used in Javascript and thus the most popular mapping libraries

For the conversion I used ogr2ogr, an open-source library for processing geospatial data. There are various conversion details related to the projection between different [coordinate systems] (http://ben.balter.com/2013/06/26/how-to-convert-shapefiles-to-geojson-for-use-on-github/), which I decided to ignore. Instead I just chose the default projection format and visually checked the resulting map images to make sure they were roughly identical. [This article] (http://ben.balter.com/2013/06/26/how-to-convert-shapefiles-to-geojson-for-use-on-github/) was useful in guiding me through the process.

The converted GeoJSON files looked like this, excluding extraneous fields:

```
{
  "type": "FeatureCollection",
  "features": [
	  {
			"type": "Feature",
			"properties": {
				"AREA" : ...,
				"PERIMETER" : ...,
				"CODE" : ...,
			},
			"geometry" : {
				"type" : "Polygon",
				"coordinates" : [ [ [-121.61, 36.21], [-121.83, 36.83], ... ] ]
			}
		},
		...
	]
```

So each tree range was a list of features (i.e. map regions), each of which had an AREA, PERIMETER, and CODE and whose geometry was given by a Polygon with a list of (longitude, latitude) coordinate pairs describing the polygon's outline. Note that the coordinates are actually a list of list of coordinate pairs - this is because sometimes the feature is of type MultiPolygon rather than Polygon, and multiple polygons are specified. I'm not quite sure why MultiPolygons aren't just split up into additional "single-Polygon" features, but it didn't seem to impact any of my results.

Github has a convenient built-in GeoJSON renderer, so you can see the [balsam fir tree's range](https://github.com/nsrivast/tree-range/blob/master/data/tree_ranges/abiebals/abiebals.geojson) and compare with [the raw file](https://raw.githubusercontent.com/nsrivast/tree-range/master/data/tree_ranges/abiebals/abiebals.geojson).

The one complication is the CODE property. CODE = 1 means the region is filled, CODE = 0 means unfilled. This allows the file to describe map holes by putting a CODE = 0 range within a CODE = 1 range. I didn't immediately know what to do with this, but it became a concern later on.

#### <a name="initial-explore1"></a>Explore format and structure of location data
The US Census Bureau maintains boundary files for various geographic areas of the country and at various resolution levels. I wanted a range of area sizes - [states] (https://www.census.gov/geo/maps-data/data/cbf/cbf_state.html), [counties] (https://www.census.gov/geo/maps-data/data/cbf/cbf_counties.html), and towns. I couldn't locate a national data source for townships, but [this article] (http://techslides.com/mapping-town-boundaries-with-d3) led me to township data for the Northeast.

After converting to GeoJSON, the data looked identical to the tree range data except without the AREA and PROPERTY fields and with additional fields, one of which was the official state or county name. I had to aggregate county and state information to obtain a unique name for each location, the details of which are in [this file] (#).

#### <a name="initial-plan"></a>Plan out rest of project and code architecture
I now had enough information to plan out the rest of the project. After downloading and converting the tree range and geographic location data to GeoJSON, I would have to intersect the two data sets, either through some polygon intersection calculation or a simplification - preliminary research brought up the possibility of a PointInPolygon algorithm that might be useful. The results of the intersection would list which tree species were present at which locations, and which locations were spanned by each species. Finally, I would have to design the visualization for these results and build it. 

### <a name="data"></a>Data Acquisition and Parsing
This step involved downloading all 678 tree shapefiles, converting them to GeoJSON format, and checking a few to make sure the converted GeoJSON regions matched the official PDF images. 

### <a name="side"></a>Side Project: Ranking Trees by Range Size
With a promising-sounding AREA field for each range feature, I thought it might be interesting to aggregate species by area and see which trees had the largest and smallest ranges.

#### <a name="side-examine"></a>Examine AREA field
I first wanted to see what AREA actually represented, as it wasn't described in the USGS metadata that accompanied the shapefiles. I examined two small elliptical regions in the Smoky Mountains and used Google Maps to measure their approximate major and minor axes. The calculated area and perimeter not only didn't match AREA and PERIMETER in any distance unit I could imagine, the area/perimeter ratios between the two regions didn't even roughly match the AREA/PERIMETER ratios. I decided to go ahead with the side project, as the relative AREA values did at least seem appropriate by visually inspecting some.

#### <a name="side-aggregate"></a>Aggregate and rank species by area. Check, explore results
I aggregated each region's AREA value for each species and looked at the largest and smallest ranges:

Rank | Largest | Smallest
:---:|:--------|:---------
0 | common juniper (_Juniperus communis_) | black calabash (_Amphitecna latifolia_)
1 | quaking aspen (_Populus tremuloides_) | Florida cupania (_Cupania glabra_)
2 | black spruce (_Picea mariana_) | rough strongbark (_Bourreria radula_)
3 | white spruce (_Picea glauca_) | balsam torchwood (_Amyris balsamifera_)
4 | paper birch (_Betula papyrifera_) | long spine acacia (_Acacia macracantha_)
5 | red osier dogwood (_Cornus stolonifera_) | bitterbush (_Picramnia pentandra_)
6 | Bebb willow (_Salix bebbiana_) | buccaneer palm (_Pseudophoenix sargentii_)
7 | balsam poplar (_Populus balsamifera_) | cinnecord (_Acacia choriophylla_)
8 | tamarack (_Larix laricina_) | West Indies satinwood (_Zanthoxylum flavum_)
9 | coyote willow (_Salix exigua_) | Florida clusia (_Clusia rosea_)

As a sanity check, I looked at the Wikipedia pages for many of these species. _Juniperus communis_: "It has the largest range of any woody plant", _Populus tremuloides_ : "the most widely distributed tree in North America", and no Wikipedia pages for smallest ones were reassuring.

### <a name="intersection"></a>Intersection Calculations

#### <a name="intersection-research"></a>Research, think on how to perform range calculation
For every tree and location, I was interested in the answer to the question: does the tree region (a set of non-overlapping polygons) cover or in some way intersect the location region (a different such set)? My first thought was to run a comprehensive polygon intersection algorithm, but the resolution of the tree range data set (roughly 1MB each) and some research on algorithms prompted me to look for a simplification. 

My next thought was to simplify one region to a set of points and calculate whether those points was located within the other region's polygons. There appeared to be a [literature] (http://en.wikipedia.org/wiki/Point_in_polygon) on the subject and some implementations that fit my requirements: a fast and simple solution in some high-level language. Because geographic locations were more regularly shaped than tree ranges, I decided to calculate the centroid of each region and check if that point existed in at least one polygon in a given tree range. I kept in mind that my results would be less accurate for larger regions (such as states), because I was only sampling the center of the region. I also considered looking at the corners of the bounding box for each region, but realized that in practically all cases those points would actually be within neighboring regions. 

#### <a name="intersection-select"></a>Select, install, test library for PolygonContainsPoint and PolygonCenter calculations
Most of the fastest implementations used databases that handled GIS data or were written in C/C++, but these [two] (http://www.mhermans.net/geojson-shapely-geocoding.html) [articles] (http://stackoverflow.com/questions/20776205/point-in-polygon-with-geojson-in-python) led me to the Shapely library for Python. I tested the algorithm for a given tree range using [testshapely.py] for some test points and it worked correctly. It was also reasonably fast, able to process all of the polygons in a tree range in less than a second.

#### <a name="intersection-build"></a>Build library to calculate centroid for locations and intersection between tree ranges and locations, run for all data
I built a code library to load and calculate the centroid of geographic locations, to load and calculate intersections between those points and tree range regions, and to store the results. I made several re-writes and speed improvements along the way, and had to fix a major bug and rerun the results. For the entire set of US counties, the largest data set, the calculations took about 2 hours on a 2.8GHz MacBook Pro.

### <a name="explore"></a>Explore Results

#### <a name="explore-produce"></a>Produce summary statistics
For the 678 tree species, the 52 states (included DC and Puerto Rico), ~3000 counties, and ______ northeast towns, summary data:

  1. 678 total trees (restrict by min area?)
  2. 52 states : 317 species included in some state
  3. 7 northeast states: 102 species total, 63 avg per state
  4. ~3000 total counties, restricted to 126 in northeast: 129 species total, 65 avg per state

#### <a name="explore-look"></a>Look for patterns and think on visualization metrics
I now had a list of all tree species contained in each region and all regions covered by each species, and began to consider how to best represent and visualize the information. Starting from the tree data, it would be somewhat interesting to see how many regions and what total area each tree covered, although I already had a good idea of that from the AREA investigation. I couldn't think of many fruitful comparisons to be made between trees besides size of coverage area, as metrics like shape, directionality, or region of coverage were probably better examined per-location than per-tree.

More interesting was to start from the location data, which could show metrics such as number of trees contained as a layer on top of the geographical data. I also thought some measure of how unique the location's species were might be interesting, especially relative to nearby regions. Could we correlate the country's geophysical regions and boundaries to features of the tree range data?

Lastly, for a more in-depth look at the universe of tree types, overlaying additional data such as broader taxonomic classifications or specific features (e.g. deciduous versus evergreen) of trees onto a map might be useful. This would require additional data sources, such as scraping some public tree [database] (http://www.fs.fed.us/database/feis/plants/tree/) organized by species.

### <a name="build"></a>Build Visualization

#### <a name="build-find"></a>Find map library for interactive visualization
There are [lots] (http://gis.stackexchange.com/questions/8032/how-do-various-javascript-mapping-libraries-compare) of mapping libraries out there. Because I wanted to avoid a commercial API, I focused on [OpenLayers and Leaflet] (http://gis.stackexchange.com/questions/33918/should-i-use-openlayers-or-leaflet). Because I needed something relatively simple, I chose Leaflet which had some [examples] (http://leafletjs.com/examples/choropleth) that seemed to be similar to my intended result. I went through some demo and documentation code for Leaflet, which works directly with GeoJSON file formats.

#### <a name="build-build"></a>Build basic visualization
My first goal was to display a set of locations on a map that included simple text data with a list of trees contained in each region. Based on Leaflet examples, I expanded my code library to insert the tree lists into a new Javascript file with data for all locations. Because I wanted to iterate through different calculations and metrics for displaying data on maps, I moved as much of the visualization parameters into pre-calculated Python code and left the map-generating Javascript as generic as possible. 

#### <a name="build-show"></a>Show tree ranges on map
Partly as a way to check my results, and partly because I wanted to visualize tree ranges on the same map as locations, I decided to include the tree range region data in the visualization. I converted the GeoJSON files into Javascript data files for each tree species, and took the opportunity to reduce the latitude and longitude precision to 0.001 degrees which reduced the file size. The files were still quite large, so I decided to load them dynamically when a tree was selected instead of upfront. 

#### <a name="build-experiment"></a>Experiment with displaying various metrics
I expanded my set of calculations to include various metrics of interest in each region - number of trees, distribution of trees, uniqueness of trees - and started looking at different regions of the country with states and counties colored by each metric. It was immediately clear that state-level location data was too coarse for informative results; California, for example, registered very few tree species only because its centroid was in the arboreally-sparse Central Valley. [CA state example] County-level data was more interesting, although looking at the full country was overwhelming. [country-level counties] I focused on the northeast states (New England + New York) whose geography I had a better intuition for. [northeast counties]

The most interesting metric I tested was arrived at after a bit of back-and-forth. I wanted a sense of how unique each county's tree population was, so I calculated a "coverage" metric for each tree species defined as the fraction of total locations in the sample in which that species was present. Then, I calculated the "average coverage" for each location across all the trees it contained. (The distribution of coverage across all trees was roughly bi-modal, with some trees appearing in almost every location, some trees appearing in very few locations, and a smaller set of trees with in-between coverage. There might be something more precise to calculate for each location than a simple average, such as: fraction of "common" trees excluded, or fraction of "uncommon" trees included. For now, I stuck withi average.)

This gave an interesting result [example], in which I could see the geographical uniqueness of the Adirondack and Acadian regions and the southern coastal regions of Connecticut and New York City. However, results were skewed for regions with fewer trees [Nevada example]. Instead of just looking at one metric, I wanted to see both average coverage and number of trees on the same map. I expanded my code to generate HSV values assigning appropriate hue and saturation values for average coverage and number of trees, respectively. The graphic looked the best with a blue/red hue gradient. [final exmample]

### <a name="final"></a>Final Improvements and Deployment

#### <a name="final-productionize"></a>Productionize and host visualization
Having decided on a metric and design for the visualization, I spent some time cleaning up the code library and wrapped into a master function the data loading and parsing, intersection algorithm, stats and coverage calculations, and javascript file creation. This allowed me to efficiently process different geographic regions and explore different portions of the country. I added some simple styling to the visualization, and I worked through various interactivity and data display bugs that had come up during website development. I also had to remove some island counties and towns that were outside of all tree ranges and messed up the coverage calculations. I hosted the whole project on GitHub and pushed the final visualization to a GitHub page, located [here] (#).

#### <a name="final-write"></a>Write this README
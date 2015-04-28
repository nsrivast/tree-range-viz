## Tree Range Visualization

### Summary
The goal of this project was to create a data exploration tool to examine the distribution of tree species across North America. I wanted an easy way to identify which trees are prevalent in different locations and geographies of the continent, without having to search through Wikipedia:Flora pages for nearby parks or cities. I also wanted to understand the range of various tree species and tree types.

### Background
In preparation for a series of section hikes of the Appalachian Trail, I wanted to familiarize myself with the most common tree species I would encounter. I found online resources on plants common to specific regions, such as local parks and forests, but no central resource that answered the question: which trees are prevalent in a given area of the country?

### Result
View the [final visualization] (http://nsrivast.github.io/tree-range-viz/), and read [an analysis of the results] (http://nsrivast.github.io/tree-range-viz/). The rest of this README explains how I built the tool, the analysis and design decisions I made along the way, and the data formats and libraries I encountered (shapefiles, geoJSON, Shapely for Python, Leaflet).

### Outline

1. [Initial Research] (#initial)

2. [Data Acquisition and Parsing] (#data)

3. [Intersection Calculations] (#intersection)

4. [Explore Results] (#explore)

5. [Build Visualization] (#build)
	
### <a name="initial"></a>Initial Research

##### <a name="initial-inspiration"></a>Inspiration for problem, initial research
Looking for resources on the ranges of tree species led me quickly to the tree range maps of [Elbert Little] (http://en.wikipedia.org/wiki/Elbert_Luther_Little), a botanist who (in his tenure as the amazingly-titled "Chief Dendrologist" of the USDA Forest Service) aggregated data from various sources to produce a set of tree range maps for 678 tree species of North America. These maps were digitized by the USGS and are available [here] (http://esp.cr.usgs.gov/data/little/) in PDF and shapefile format. [Here's](https://github.com/nsrivast/tree-range-viz/blob/master/data/tree_ranges/abiebals/abiebals.pdf) an example of a range map for the balsam fir:

##### <a name="initial-explore"></a>Explore format and structure of tree data
Little's tree ranges are represented by shapefiles, a common format in the well-developed field of [Geographic Information Systems (GIS)] (http://en.wikipedia.org/wiki/Geographic_information_system). After downloading and examining the shapefiles, and after some research and deliberation, I decided to convert the shapefiles to the GeoJSON format, for a few reasons: 

* it is a lighter format, and I only needed the basic outlines of the tree ranges
* it is easier to parse as a human reader
* it is a JSON format, easily used in Javascript and the most popular mapping libraries

For the conversion I used ogr2ogr, an open-source library for processing geospatial data. There are various conversion details related to the projection between different [coordinate systems] (http://maps.unomaha.edu/Peterson/gis/notes/MapProjCoord.html) - [this article] (http://ben.balter.com/2013/06/26/how-to-convert-shapefiles-to-geojson-for-use-on-github/) was useful in guiding me through the process.

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

Each tree range was represented by a list of features (map regions), each of which had an AREA, PERIMETER, and CODE and whose geometry was given by a Polygon with a list of (longitude, latitude) coordinate pairs describing the polygon's outline. Note that the coordinates are actually a list of list of coordinate pairs - this is because sometimes the feature is of type MultiPolygon rather than Polygon, and more than one polygon is listed.

Github has a convenient built-in GeoJSON renderer, so you can see the [balsam fir tree's range](/data/tree_ranges/abiebals/abiebals.geojson) and compare with [the GeoJSON data](/data/tree_ranges/abiebals/abiebals.geojson).

The one complication is the CODE property. CODE = 1 means the region is filled, CODE = 0 means unfilled. This allows the file to describe map holes by putting a CODE = 0 range within a CODE = 1 range. I didn't immediately know what to do with this, but it became a concern later on.

##### <a name="initial-explore1"></a>Explore format and structure of location data
The US Census Bureau maintains boundary files for various geographic areas of the country and at various resolution levels. I wanted a range of area sizes - [states] (https://www.census.gov/geo/maps-data/data/cbf/cbf_state.html), [counties] (https://www.census.gov/geo/maps-data/data/cbf/cbf_counties.html), and towns. I couldn't locate a national data source for townships, but [this article] (http://techslides.com/mapping-town-boundaries-with-d3) led me to township data for the Northeast.

After converting to GeoJSON, the data looked identical to the tree range data except without the AREA and PROPERTY fields and with sevearl additional fields, one of which was the official state or county name. I aggregated county and state information to obtain a unique name for each location.

##### <a name="initial-plan"></a>Plan out rest of project and code architecture
I now had enough information to plan out the rest of the project. After downloading and converting the tree range and geographic location data to GeoJSON, I would intersect the two data sets, either through some polygon intersection calculation or a simplification. The results of the intersection would list which tree species were present at which locations, and which locations were spanned by each species. Next, I would explore the data to identify which metrics were most informative. Finally, I would design the visualization to show these metrics and build and test it.

### <a name="data"></a>Data Acquisition and Parsing
This step involved downloading all 678 tree range shapefiles and the thousands of location shapefiles, converting them to GeoJSON format, and checking a few visually to make sure the converted GeoJSON regions were sensible. 

### <a name="intersection"></a>Intersection Calculations

##### <a name="intersection-research"></a>Research, think on how to perform range calculation
For every tree and location, I was interested in the answer to the question: does the tree region (a set of non-overlapping polygons) cover or in some way intersect the location region (a different set of polygons)? My first thought was to run an exhaustive polygon intersection algorithm, but the resolution of the tree range data set (roughly 1MB each) and some research on algorithms prompted me to look for a simplification. 

My next thought was to simplify one region to one point or a set of points and calculate whether those points were located within the other region's polygons. There appeared to be a [literature] (http://en.wikipedia.org/wiki/Point_in_polygon) on the subject and some implementations that fit my requirements. Because geographic locations were more regularly shaped than tree ranges, I decided to calculate the centroid of each region and calculate if that point existed in at least one polygon for a given tree range. I kept in mind that my results would be less accurate for larger regions (such as states), because I was only sampling the center of the region. I also considered looking at the corners of the bounding box for each region, but realized that those points would usually be in neighboring regions. 

##### <a name="intersection-select"></a>Select, install, test library for PolygonContainsPoint and PolygonCenter calculations
Most of the fastest implementations used customized databases that handled GIS data or were written in C/C++, but these [two] (http://www.mhermans.net/geojson-shapely-geocoding.html) [articles] (http://stackoverflow.com/questions/20776205/point-in-polygon-with-geojson-in-python) led me to the Shapely library for Python. I tested the algorithm with a test tree range and some sample points and it seemed to work correctly. It was also reasonably fast, able to process all of the polygons in a tree range in less than a second.

##### <a name="intersection-build"></a>Build library to calculate centroid for locations and intersection between tree ranges and locations, run for all data
I write code to load and calculate the centroid of geographic locations, to load and calculate intersections between those points and tree range regions, and to store the results. For the entire set of northeast townships, the largest data set, the calculations took about 2.5 hours on a 2.8GHz MacBook Pro.

### <a name="explore"></a>Explore Results

##### <a name="explore-look"></a>Examine data and think on visualization metrics
For the 678 tree species, the 50 states, ~3000 counties, and ~3500 northeast towns, I had a list of all tree species contained in each region and all regions covered by each species. The next step was to consider how to best represent and visualize the information.

Starting from the tree data, it would be somewhat interesting to see how many regions and what total area each tree covered, although this information was already given my the tree range maps. I couldn't think of many fruitful comparisons to be made between trees besides size of coverage area, as metrics like shape, directionality, or region of coverage were probably better examined per-location than per-tree.

More interesting was to start from the location data, which could show metrics such as number of trees contained as a layer on top of the geographical data. I also thought some measure of how unique the location's species were might be interesting, especially relative to nearby regions. Could we correlate the country's geophysical regions and boundaries to features of the tree range data?

Lastly, for a more in-depth look at the universe of tree types, overlaying additional data such as broader taxonomic classifications or specific features (e.g. deciduous versus evergreen) of trees onto a map might be useful. This would require additional data sources, such as scraping some public tree [database] (http://www.fs.fed.us/database/feis/plants/tree/) organized by species.

### <a name="build"></a>Build Visualization

##### <a name="build-find"></a>Find map library for interactive visualization
There are [lots] (http://gis.stackexchange.com/questions/8032/how-do-various-javascript-mapping-libraries-compare) of mapping libraries out there. Because I wanted to avoid a commercial API, I focused on [OpenLayers and Leaflet] (http://gis.stackexchange.com/questions/33918/should-i-use-openlayers-or-leaflet). Because I needed something relatively simple, I chose Leaflet which had some [examples] (http://leafletjs.com/examples/choropleth) that seemed to be similar to my intended result. I went through some demo and documentation code for Leaflet.

##### <a name="build-build"></a>Build basic visualization, experiment with various metrics
I wrote code to calculate various metrics of interest in each region (number of trees, distribution of trees, uniqueness of trees) and started looking at different regions of the country with states and counties colored by each metric. It was immediately clear that state-level location data was too coarse for informative results; California, for example, registered very few tree species only because its centroid was in the arboreally-sparse Central Valley. County-level data was more interesting, although looking at the full country was overwhelming. I focused on counties in different regions, such as the northeast states whose geography I had a better intuition for.

The most interesting metric I devised attempted to measure how unique each county's tree population was. I calculated a "coverage" metric for each tree species defined as the fraction of total locations in the sample for which that species was present. Then, I calculated the "average coverage" for each location across all the trees it contained. This gave interesting results, in which I could see the geographical uniqueness of the Adirondack and Acadian regions and the southern coastal regions of Connecticut and New York City. However, results were skewed for regions with fewer trees whose average had higher variance.

Wanting to see average coverage normalized by number of trees, I assigned color based on average coverage and lightness/darkness based on number of trees. This resulting visualization produced the set of graphics described in [this analysis] (http://nsrivast.github.io/tree-range-viz/)
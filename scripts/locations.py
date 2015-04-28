# LOCATIONS
#
# loads, parses geoJSON files representing geographic areas (states, counties, townships)

import pdb
import json
from shapely.geometry import shape, Point


FILENAME_STATES = 'data/states/cb_2013_us_state_20m.geojson'
FILENAME_COUNTIES = 'data/counties/cb_2013_us_county_20m.geojson'
STATE_FILTERS = {
    'ne' : ["09", "23", "25", "33", "36", "44", "50"],
    'ma' : ["36", "42", "34", "10", "24"],
    'ca' : ["06"],
    'ny' : ["36"]
}
TOWN_UNIQID_FNS = {
    'ct' : lambda x: '%s, CT' % x['TNA'],
    'ma' : lambda x: '%s, MA' % x['TOWN'],
    'me' : lambda x: '%s, ME' % x['TOWN'],
    'nh' : lambda x: '%s, NH' % x['NAME'],
    'ny' : lambda x: str(x['LABEL']) + ' (' + str(x['SWIS']) + '), NY',
    'ri' : lambda x: '%s, RI' % x['NAME'],
    'vt' : lambda x: '%s, VT' % x['TOWNNAME']
}

def load_location_data_from_file(fname, uniqid_fn):
    """ Loads and parses location data:
    
    - opens geoJSON file
    - applies UNIQID function
    - removes nulls/duplicates
    - adds centroid LNGLAT location
    
    """
    # open file
    with open(fname, 'r') as f:
        locs_json = json.loads(unicode(f.read(), "ISO-8859-1"))    
    locs = locs_json['features']
    
    # apply UNIQID function
    for loc in locs:
        loc['properties']['UNIQID'] = uniqid_fn(loc['properties'])
        
    # remove null/duplicate
    used_UNIQIDs = set()
    new_locs = []
    for loc in locs:
        uniqid = loc['properties']['UNIQID']
        if (uniqid is not None) and (uniqid not in used_UNIQIDs):
            new_locs.append(loc)
            used_UNIQIDs.add(loc['properties']['UNIQID'])
    locs = new_locs
    
    # adds centroid
    for loc in locs:
        polygon = shape(loc['geometry'])
        loc['properties']['LNGLAT'] = (polygon.centroid.x, polygon.centroid.y)
    
    return locs
    
    
def load_state_data(locs_filter=False):
    """ Loads state data, optionally filter by state. """
    locs = load_location_data_from_file(FILENAME_STATES, lambda x: x['NAME'])
    if locs_filter:
        locs = filter(lambda x: x['properties']['STATEFP'] in STATE_FILTERS[locs_filter], locs)
    return locs


def load_county_data(locs_filter=False):
    """ Loads county data, optionally filter by state."""
    locs = load_location_data_from_file(FILENAME_COUNTIES, lambda x: x['NAME'] + ' (' + x['COUNTYFP'] + ')')
    if locs_filter:
        locs = filter(lambda x: x['properties']['STATEFP'] in STATE_FILTERS[locs_filter], locs)
    return locs
    
    
def load_town_data(locs_filter=False):
    """ Loads town data for northeast states. """
    
    if locs_filter:
        locs = load_location_data_from_file( 'data/towns/' + locs_filter + '_towns.geojson', TOWN_UNIQID_FNS[locs_filter] )
    else:
        locs = []
        for state, uniqid_fn in TOWN_UNIQID_FNS.items():
            locs += load_location_data_from_file( 'data/towns/' + state + '_towns.geojson', uniqid_fn )

    return locs


def load_all_data():
    """ Loads all location data in tuple """

    states = load_state_data(False)
    states_ne = load_state_data("ne")
    counties = load_county_data(False)
    counties_ne = load_county_data("ne")    
    towns = load_town_data(False)
    
    return states, states_ne, counties, counties_ne, towns
    

def load_location_data(locs_tag, locs_filter=False):
    """ Loads location data given location tag (states, counties, towns) and optional filter. """
    if locs_tag == "states":
        res = load_state_data(locs_filter)
    elif locs_tag == "counties":
        res = load_county_data(locs_filter)
    elif locs_tag == "towns":
        res = load_town_data(locs_filter)
    else:
        raise NameError("unsupported location tag")
    return res
    

if __name__ == "__main__":
    
    states, states_ne, counties, counties_ne, towns = load_all_data()
    
    print "Loaded %s states." % len(states)
    print "Loaded %s states (northeast)." % len(states_ne)
    print "Loaded %s counties." % len(counties)
    print "Loaded %s counties (northeast)." % len(counties_ne)
    print "Loaded %s towns (northeast)." % len(towns)

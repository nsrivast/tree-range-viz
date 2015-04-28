# INTERSECTIONS
#
# calculates intersections between tree ranges and geographic areas (states, counties, townships)

import pdb
import locations
import treeranges
import time
import sys
import os
import pickle
from shapely.geometry import shape, Point

def log(s, verbose=False):
    if verbose:
        sys.stdout.write(s)
        sys.stdout.flush()
        
def calculate_intersections(locs_data, tree_data):
    """ Constructs and returns:
    
    - trees_locs: for each tree, list of locations covered
    - locs_trees: for each location, list of trees contained
    
    Trees are labeled by shortname and locations by UNIQID.
    """
    
    # initialize empty dicts for all locations, species
    trees_locs = { shortname: [] for shortname in tree_data }
    locs_trees = { loc['properties']['UNIQID']: [] for loc in locs_data }
    
    # for each tree ...
    for shortname in tree_data:
        range_features = tree_data[shortname]['range_features']
        range_polygons = [shape(feature['geometry']) for feature in range_features]
        
        # for each location ...
        for loc in locs_data:
            loc_id = loc['properties']['UNIQID']
            lnglat = loc['properties']['LNGLAT']
            
            # check if at least one range polygon contains centroid.
            i = 0
            found = False
            while not found and i < len(range_polygons):
                range_polygon = range_polygons[i]
                found = range_polygon.contains(Point(lnglat))
                i += 1
            
            if found:
                trees_locs[shortname] += [loc_id]
                locs_trees[loc_id] += [shortname]   

        log(shortname + ", ", True)
            
    print("\n")
    return trees_locs, locs_trees


def run_and_save_intersections(locs_data, tree_data, fname):
    """ Runs and saves results for location/tree intersections """    
    t0 = time.time()
    trees_locs, locs_trees = calculate_intersections(locs_data, tree_data)        
    print time.time() - t0, " seconds"
    
    with open(fname, 'w') as f:
        pickle.dump([trees_locs, locs_trees], f)    
        
    return trees_locs, locs_trees


def load_intersections(fname):
    """ Loads location/tree intersections from file """    
    with open(fname) as f:
       trees_locs, locs_trees = pickle.load(f)
    return trees_locs, locs_trees


def calc_or_load_intersections(locs_tag, trees_tag, locs_filter=False):
    """ Looks for and loads intersections data file, if not found then runs intersections. """
    fname = locs_tag + ("_" + locs_filter if locs_filter else "") + trees_tag
    fname = "results/intersections/" + fname + ".dict"
    if os.path.isfile(fname):
        print "-- Existing intersection results found."
        trees_locs, locs_trees = load_intersections(fname)
    else:
        print "-- Running intersection calculations and saving results."
        locs_data = locations.load_location_data(locs_tag, locs_filter)
        trees_data = treeranges.load_tree_data(trees_tag)
        trees_locs, locs_trees = run_and_save_intersections(locs_data, trees_data, fname)
    return trees_locs, locs_trees
    
    
if __name__ == "__main__":
    
    locs_tag = "states"
    locs_filter = "ne"
    trees_tag = "_trunc"
    
    trees_data = treeranges.load_tree_data(trees_tag)
    locs_data = locations.load_location_data(locs_tag, locs_filter)
    
    t0 = time.time()
    trees_locs, locs_trees = calculate_intersections(locs_data, trees_data)
    print time.time() - t0, " seconds for calcs"
    
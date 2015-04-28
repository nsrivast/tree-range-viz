# TREERANGES
#
# loads, parses geoJSON files representing ranges of trees
#
# each tree has:
# - shortname: name abbreviation of 8 characters (dictionary key)
# - common: common english name
# - species: latin species name
# - range_features: list of geoJSON features
#

import pdb
import csv
import json


FILENAME_FN = lambda shortname: 'data/tree_ranges/%s/%s.geojson' % (shortname, shortname)
JS_FILENAME_FN = lambda shortname: 'data/tree_ranges/%s/%s.js' % (shortname, shortname)

with open('data/tree_names.csv', 'r') as f:
    tree_names = [row for row in csv.reader(f.read().splitlines())]
    
SHORTNAME_COMMON = { shortname: common for shortname, dum, common in tree_names }
SHORTNAME_SPECIES = { shortname: species for shortname, species, dum in tree_names }


def lookup_common(shortname):
    return SHORTNAME_COMMON[shortname]


def lookup_species(shortname):
    return SHORTNAME_SPECIES[shortname]


def load_tree_data_from_file(fname):
    """ Loads range geoJSON data for trees in file. """    
    tree_data = {}
    shortnames = [line.rstrip('\n') for line in open(fname, 'r')]
    for shortname in shortnames:
        with open(FILENAME_FN(shortname), 'r') as f:
            tree_range_json = json.loads(unicode(f.read(), "ISO-8859-1"))['features']
            tree_data[shortname] = { 
                'shortname' : shortname, 
                'species' : SHORTNAME_SPECIES[shortname], 
                'common' : SHORTNAME_COMMON[shortname],
                'range_features' : tree_range_json
            }
    return tree_data


def load_tree_data(trees_tag):
    """ Loads location data given location tag ('', '_trunc'). """    
    tree_data = load_tree_data_from_file('data/shortnames' + trees_tag + '.txt')
    return tree_data


def trunc_list_of_floats(l_old):
    """ Recurses through list (of list (of list ... )) of floats, truncating to 3 decimal precision"""
    if type(l_old) is list:
        # empty or non-empty list
        l_new = [trunc_list_of_floats(x) for x in l_old]
    else: 
        # float
        l_new = format(l_old, '.3f')
    return l_new
    

def treeranges_to_js(trees_tag):
    """ Writes tree range data to .js file for each tree, truncating lat/long to 3 decimal precision. """
    fname = 'data/shortnames' + trees_tag + '.txt'
    shortnames = [line.rstrip('\n') for line in open(fname, 'r')]
    
    for shortname in shortnames:
        with open(FILENAME_FN(shortname), 'r') as f:
            tree_range_json = json.loads(unicode(f.read(), "ISO-8859-1"))
            for feature in tree_range_json['features']:
                feature['geometry']['coordinates'] = trunc_list_of_floats(feature['geometry']['coordinates'])
        
        full_str = "var treeRange" + shortname + " = " + json.dumps(tree_range_json) + ";"        
        with open(JS_FILENAME_FN(shortname), 'w') as f:
            f.write(full_str)
        
    return True    


if __name__ == "__main__":

    #tree_data = load_tree_data('_trunc')    
    #print "Loaded %s trees." % len(tree_data)
    
    treeranges_to_js("_trunc")
    
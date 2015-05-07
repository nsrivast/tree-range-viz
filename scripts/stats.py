# STATS
#
# calculates statistics on intersection data, such as coverage fractions

import pdb
import intersections
import treeranges
import map_settings

def load_dicts(fname):
    """ Loads location/tree dicts from file """    
    with open(fname) as f:
       trees_locs, locs_trees = pickle.load(f)
       
    return trees_locs, locs_trees

    
def calc_stats(trees_locs, locs_trees):
    """ Calculates statistics for locations and trees using intersection data, returning dict:
    
    - trees_stats: { shortname: (common name, species name, [locations], n_locations, coverage) }
    - locs_stats: { loc_id: ([shortnames], n_trees, avg_coverage) }
    
    locs_stats: (location name, [shortnames], n trees, avg coverage fraction for its trees)    
    tree_stats: (tree, [locations], n locations, coverage fraction)
    """
    
    n_locs = len(locs_trees)
    
    trees_stats = {}
    for shortname, locs in trees_locs.items():
        trees_stats[shortname] = {
            'shortname' : shortname,
            'common_name' : treeranges.lookup_common(shortname), 
            'species_name' : treeranges.lookup_species(shortname),
            'locations' : locs,
            'n_locations' : len(locs),
            'coverage' : (0.0 + len(locs))/n_locs            
        }
    
    locs_stats = {}
    for loc_id, shortnames in locs_trees.items():
        locs_stats[loc_id] = {
            'shortnames' : shortnames,
            'n_trees' : len(shortnames),
            'avg_coverage': 0
        }
        if len(shortnames) > 0:
            cfs = [trees_stats[shortname]['coverage'] for shortname in shortnames]
            locs_stats[loc_id]['avg_coverage'] = sum(cfs)/len(cfs)
    
    
    color_map = map_settings.gen_color_map_max_sat(trees_stats)
    for shortname, locs in trees_locs.items():
        trees_stats[shortname]['color'] = color_map(trees_stats[shortname]['coverage'])
    
    all_stats = { 'trees_stats' : trees_stats, 'locs_stats' : locs_stats }
    
    return all_stats


def add_stats_to_locs(locs_data, stats):
    """ Sets properties field for locations with fields needed in map: 
    
    - Name: loc_id
    - Description: [Name] \n ([n_trees] trees, [avg_coverage] average coverage)
    - ShortDescription: [Name] ([n_trees], [avg_coverage])
    - Color: calculated fill color based on n_trees, avg_coverage
    - TreeTable: [(common name, coverage, shortname)] in ascending coverage order
    
    """
    color_map = map_settings.gen_color_map(stats['locs_stats'])
    
    locs_data_withstats = locs_data[:]
    for loc in locs_data_withstats:
        loc_id = loc['properties']['UNIQID']
        loc_stats = stats['locs_stats'][loc_id]
        n_trees = loc_stats['n_trees']
        avg_coverage = loc_stats['avg_coverage']
        color = color_map(n_trees, avg_coverage)
        description = '<b>' + loc_id + '</b><br /> (%s trees, %s average coverage)' % (n_trees, "{0:.0f}%".format(avg_coverage*100))
        short_description = '<b>' + loc_id + '</b> (%s, %s)' % (n_trees, "{0:.0f}%".format(avg_coverage*100))
        
        has_trees_stats = [stats['trees_stats'][shortname] for shortname in loc_stats['shortnames']]
        tree_list_data = [ (x['common_name'], x['coverage'], x['shortname'], x['color']) for x in has_trees_stats]        
        tree_list_data.sort(key=lambda x: x[1])
        tree_table = [ (a, "{0:.0f}%".format(b*100), c, d) for a,b,c,d in tree_list_data ]
        
        loc['properties'] = { 
            'Name': loc_id, 
            'Description': description, 
            'ShortDescription': short_description, 
            'Color' : color, 
            'TreeTable' : tree_table,
            'title': description
        }
    
    return locs_data_withstats
    
    
def print_stats(trees_stats, locs_stats):
    n_locs = len(locs_stats)
    n_locs_incl = len(filter(lambda x: x[1], locs_stats))

    n_trees = len(trees_stats)
    n_trees_incl = len(filter(lambda x: x[1], trees_stats))
    n_trees_per_loc = sum([loc_stats[2] for loc_stats in locs_stats])/n_locs
    
    print "==== Counts ===="
    print "%s Total Trees, %s Included in Locations, %s Average Trees per Location" % (n_trees, n_trees_incl, n_trees_per_loc)
    print "%s Total Locations" % n_locs
    
    n_incl = 5

    print "\n==== Sorted Locations ===="
    locs_by_n_trees = ["%s (%s)" % (loc, count) for loc, dumA, count, dumB in sorted(locs_stats, key=lambda x: -x[2])]
    print " >> Locations with Most Trees: " + ", ".join(locs_by_n_trees[:n_incl])
    print " >> Locations with Least Trees: " + ", ".join(locs_by_n_trees[-n_incl:])

    locs_by_cf = ["%s (%s)" % (loc, cf) for loc, dumA, dumB, cf in sorted(locs_stats, key=lambda x: -x[3])]
    print " >> Locations with Highest Average Coverage Fraction: " + ", ".join(locs_by_cf[:n_incl])
    print " >> Locations with Lowest Average Coverage Fraction: " + ", ".join(locs_by_cf[-n_incl:])

    print "\n==== Sorted Trees ===="
    trees_by_n_locs = ["%s (%s)" % (treeranges.lookup_common(tree), count) for tree, dumA, count, dumB in sorted(trees_stats, key=lambda x: -x[2])]
    print " >> Trees with Most Locations: " + ", ".join(trees_by_n_locs[:n_incl])
    print " >> Trees with Least Locations: " + ", ".join(trees_by_n_locs[-n_incl:])
    
    trees_by_cf = ["%s (%s)" % (treeranges.lookup_common(tree), avg_cf) for tree, dumA, dumB, avg_cf in sorted(trees_stats, key=lambda x: -x[3])]
    print " >> Trees with Highest Coverage Fraction: " + ", ".join(trees_by_cf[:n_incl])
    print " >> Trees with Lowest Coverage Fraction: " + ", ".join(trees_by_cf[-n_incl:])
    
    
if __name__ == "__main__":
    
    locs_tag = "counties"
    locs_filter = "ne"
    trees_tag = ""
    
    trees_locs, locs_trees = intersections.calc_or_load_intersections(locs_tag, trees_tag, locs_filter)
    all_stats = calc_stats(trees_locs, locs_trees)
    
    for shortname, data in all_stats['trees_stats'].items():
        print shortname + ", " + str(data['coverage'])
    
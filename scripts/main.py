# ANALYSIS
# 
# exploring intersections results data

import pdb
import intersections
import locations
import stats
import geojson
import map_settings

UNIQIDS_TO_FILTER = ['Cecil (015)', "Barnstable (001)", "None, CT", "CHILMARK, MA", "Atlantic Beach (282043), NY", "Island Park (282021), NY", "PORTSMOUTH, RI", 'EDGARTOWN, MA', 'WELLFLEET, MA', 'NAHANT, MA', 'CHATHAM, MA', 'BOSTON, MA', 'GOSNOLD, MA', 'DUXBURY, MA', 'SCITUATE, MA', 'YARMOUTH, MA', 'HARWICH, MA', 'SALEM, MA', 'MARBLEHEAD, MA', 'OAK BLUFFS, MA', 'BARNSTABLE, MA', 'WEYMOUTH, MA', 'TISBURY, MA', 'HINGHAM, MA', 'NEWBURYPORT, MA', 'GLOUCESTER, MA', 'MANCHESTER, MA']
UNIQIDS_TO_FILTER += ['IsleAuHaut, ME', 'VinalHaven, ME', 'SwansIsland, ME', 'Breman, ME', 'MatinicusIslePlt, ME', 'NorthHaven, ME', 'WinterHarbor, ME', 'StGeorge, ME', 'CranberryIsles, ME', 'Arrowsic, ME', 'MonheganPlt, ME', 'Friendship, ME', 'Southport, ME', 'BoothbayHarbor, ME', 'Beals, ME', 'Cushing, ME', 'SouthBristol, ME', 'DeerIsle, ME', 'Harrington, ME', 'Cutler, ME', 'Kittery, ME', 'WestBath, ME', 'Frenchboro, ME']
UNIQIDS_TO_FILTER += ['Ocean Beach (472803), NY', 'Saltaire (472805), NY', 'Manor Haven (282221), NY', 'Manhattan (620000), NY', 'Kings (610000), NY', 'Hewlett Harbor (282017), NY', 'Long Beach (281000), NY', 'Brookhaven (472200), NY', 'Bronx (600000), NY', 'Hewlett Neck (282019), NY', 'Westhamp Beach (473607), NY', 'Quogue (473603), NY', 'Baxter Estates (282201), NY', 'Poquott (472209), NY', 'Croton-On-Hud (552203), NY']

def filter_out_uniqids(locs_data, locs_trees, uniqids):
    ''' Removes locations by UNIQID from data files and intersection results '''

    locs_data_filtered = locs_data[:]
    locs_trees_filtered = locs_trees.copy()

    for uniqid in uniqids:
        locs_data_filtered = filter(lambda loc: not (loc['properties']['UNIQID'] == uniqid), locs_data_filtered)
        locs_trees_filtered.pop(uniqid, None)
    
    return locs_data_filtered, locs_trees_filtered
    
    
def rewrite_js(locs_tag, trees_tag, locs_filter=False):
    ''' Loads location and intersection data, calculates statistics and map parameters, saves to .js '''
    
    print("\nWriting .js files for (%s, %s, %s) ..." % (locs_tag, trees_tag, locs_filter))
    
    print("- Loading location and intersection data, filtering out low-volume locations")
    locs_data = locations.load_location_data(locs_tag, locs_filter)
    trees_locs, locs_trees = intersections.calc_or_load_intersections(locs_tag, trees_tag, locs_filter)
    locs_data, locs_trees = filter_out_uniqids(locs_data, locs_trees, UNIQIDS_TO_FILTER)
    
    # ma
#    print("- Filtering out low-tree regions")
#    all_stats = stats.calc_stats(trees_locs, locs_trees)
#    locs_by_n_trees = [(loc, loc_stat['n_trees']) for loc, loc_stat in all_stats['locs_stats'].items()]
#    locs_to_remove = [ loc for loc, n_trees in filter(lambda x: x[1] <= 5, locs_by_n_trees)]
#    locs_data, locs_trees = filter_out_uniqids(locs_data, locs_trees, locs_to_remove)

    print("- Calculating stats and map parameters, creating .js data")
    all_stats = stats.calc_stats(trees_locs, locs_trees)
    locs_data_withstats = stats.add_stats_to_locs(locs_data, all_stats)
    map_vars = map_settings.map_vars(locs_tag, locs_filter)
    
#    locs_by_n_trees = [(loc, loc_stat['n_trees']) for loc, loc_stat in all_stats['locs_stats'].items()]
#    locs_to_remove = [ loc for loc, n_trees in filter(lambda x: x[1] < 5, locs_by_n_trees)]
#    pdb.set_trace()
    
    print("- Saving .js to file")
    fname = locs_tag + ("_" + locs_filter if locs_filter else "") + trees_tag
    map_js_fname = "../data_locs/" + fname + ".js"
    geojson.write_to_js(locs_data_withstats, map_js_fname, "locsData", map_vars)


if __name__ == "__main__":
    
    # Custom parameters
    if False:
        rewrite_js("states", "")
        rewrite_js("states", "", "ne")
        rewrite_js("counties", "")
        rewrite_js("counties", "", "ne")
        rewrite_js("counties", "", "ma")
        rewrite_js("counties", "", "ca")
        rewrite_js("counties", "", "ny")
        rewrite_js("towns", "", "ct")
        rewrite_js("towns", "", "ma")
        rewrite_js("towns", "", "me")
        rewrite_js("towns", "", "nh")
        rewrite_js("towns", "", "ny")
        rewrite_js("towns", "", "ri")
        rewrite_js("towns", "", "vt")
        rewrite_js("towns", "")
    else:
        rewrite_js("towns", "")
        
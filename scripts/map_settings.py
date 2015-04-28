# MAP SETTINGS
#
# default map parameters for various visualizations

import colorsys

def hsv_to_hex(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return '#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255))


def gen_color_map(locs_stats):
    """ Generates color breaks using distribution of n_trees (sats) and avg_coverage (hues) """
    
    interp = lambda x, x_min, x_max, y_min, y_max: (0.0 + x - x_min)/(x_max - x_min) * (y_max - y_min) + y_min
    
    sats_min = 0.1
    sats_max = 1.0
    ns_trees = [ v['n_trees'] for k, v in locs_stats.items()]    
    n_trees_min = min(ns_trees)
    n_trees_max = max(ns_trees)
    sat_map = lambda n_trees: interp(n_trees, n_trees_min, n_trees_max, sats_min, sats_max)
    
    hues_min = 0.67
    hues_max = 0.99
    avgs_coverage = [ v['avg_coverage'] for k, v in locs_stats.items()]
    avg_coverage_min = min(avgs_coverage)
    avg_coverage_max = max(avgs_coverage)
    hue_map = lambda avg_coverage: interp(avg_coverage, avg_coverage_min, avg_coverage_max, hues_min, hues_max)
    
    color_map = lambda n_trees, avg_coverage: hsv_to_hex(hue_map(avg_coverage), sat_map(n_trees), 1.0)
    return color_map    


def gen_color_map_max_sat(trees_stats):
    """ Generates color breaks using distribution of n_trees (sats) and avg_coverage (hues) """
    
    interp = lambda x, x_min, x_max, y_min, y_max: (0.0 + x - x_min)/(x_max - x_min) * (y_max - y_min) + y_min

    hues_min = 0.67
    hues_max = 0.99
    coverages = [ v['coverage'] for k, v in trees_stats.items()]
    coverage_min = min(coverages)
    coverage_max = max(coverages)
    hue_map = lambda coverage: interp(coverage, coverage_min, coverage_max, hues_min, hues_max)
    
    color_map = lambda coverage: hsv_to_hex(hue_map(coverage), 1.0, 1.0)
    return color_map    


def map_view(locs_tag, locs_filter):
    """ Returns appropriate map center and zoom for different map types """
    if locs_filter == "ne":
        res = (44, -74, 6)
    elif locs_filter == "ca":
        res = (37.25, -120, 6)
    elif locs_tag == "counties" and locs_filter == "ma":
        res = (42, -76, 6)
    elif locs_tag == "towns" and locs_filter == "ma":
        res = (42, -72, 8)
    elif locs_filter == "ny":
        res = (42.9, -76, 7)
    elif locs_filter == "me":
        res = (45.5, -70, 7)
    elif locs_filter == "ct":
        res = (41.5, -73, 8)
    elif locs_filter == "ri":
        res = (41.5, -71.5, 9)
    elif locs_filter == "vt":
        res = (44, -73.2, 8)
    elif locs_filter == "nh":
        res = (44, -71, 7)
    else:
        res = (40, -96, 4)

    return res


def map_title(locs_tag, locs_filter):
    title = "North American Tree Distribution - "
    if locs_tag == "states":
        title += "US States"
    elif locs_tag == "states_ne":
        title += "US States (Northeast)"
    elif locs_tag == "counties":
        title += "US Counties"
    elif locs_tag == "counties_ne":
        title += "US Counties (Northeast)"
    elif locs_tag == "towns":
        title += "US Towns (Northeast)"
    else:
        raise NameError("unsupported location type")
    return title


def map_vars(locs_tag, locs_filter=False):
    """ Obtains and assembles map styling variables """
    view = map_view(locs_tag, locs_filter)
    title = map_title(locs_tag, locs_filter)
    
    map_vars = zip(['mapLat', 'mapLng', 'mapZoom'], view) + [('mapTitle', title)]
    return map_vars    
    
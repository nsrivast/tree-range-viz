# GEOJSON
#
# methods for preparing and writing .geojson files (and associated .js files)

import pdb
import intersections
import treeranges
import json


def write_to_js(locs_data, fname, suffix, js_var_name, additional_vars=[]):
    """ Writes data in locs to .js file.
    
    Assuming inputs:
    - js_var_name = "locsData"
    - additional_vars = [('firstVar', {'a': '1'}), ('secondVar', {'b': '2'})]
    - suffix = "_ne"
    
    Output will look like:
    var firstVar_ne = {'a': '1'};
    var secondVar_ne = {'b': '2']};
    var locsData_ne = ...;
    """
    for loc_data in locs_data:
        loc_data['selected'] = False
        
    data_var = [(js_var_name, { "type" : "FeatureCollection", "features" : locs_data })]
    all_vars = additional_vars + data_var
    full_str = "\n".join(["var " + varName + "_" + suffix + " = " + json.dumps(varData) + ";" for varName, varData in all_vars])
    with open(fname, 'w') as f:
        f.write(full_str)

    return True
    
    
if __name__ == "__main__":
    
    print "OK"

// === Initialize map with default location and zoom, tile layer

var map = L.map('map', { zoomControl: false }).setView([mapLat, mapLng], mapZoom);

L.tileLayer('https://{s}.tiles.mapbox.com/v3/{id}/{z}/{x}/{y}.png', {
	maxZoom: 12,
	attribution: '<a href="http://openstreetmap.org">OpenStreetMap</a> | <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a> | <a href="http://mapbox.com">Mapbox</a> | <a href="http://esp.cr.usgs.gov/data/little/">USGS</a>',
	id: 'examples.map-20v6611k'
}).addTo(map);

new L.Control.Zoom({ position: 'topleft' }).addTo(map);

// === Add legend with regional maps

var legend = L.control({position: 'bottomleft'});
legend.onAdd = function (map) {
	var div = L.DomUtil.create('div', 'legend');
	div.innerHTML = '<b>Regional Maps</b> (click twice to load)<br/>';
	
	var regionData = [
		['State', [['all', 'states']]],
		['County', [['all', 'counties'], ['north-east', 'counties_ne'], ['mid-atl', 'counties_ma'], ['CA', 'counties_ca'], ['NY', 'counties_ny']]],
		['Town', [['CT', 'towns_ct'], ['MA', 'towns_ma'], ['ME', 'towns_me'], ['NH', 'towns_nh'], ['NY', 'towns_ny'], ['RI', 'towns_ri'], ['VT', 'towns_vt']]]
	]
	
	for(var i = 0; i < regionData.length; i++) {
		var regionType = regionData[i][0]
		var regionLinks = regionData[i][1]
		
		div.appendChild(document.createTextNode(regionType + ': '));	
		
		for(var j = 0; j < regionLinks.length; j++) {
			var regionLink = document.createElement('a');
			regionLink.setAttribute("href", "#");
			regionLink.appendChild(document.createTextNode(regionLinks[j][0]));
			regionLink.setAttribute('onclick', 'loadRegion("' + regionLinks[j][1] + '")');
			
			div.appendChild(regionLink);
			div.appendChild(document.createTextNode(" "));
		}

		div.appendChild(document.createElement('div'));
	}

	return div;
};
legend.addTo(map);

// === Tree Table
	
function populateTable(p) {
	var treeTable = document.getElementById('treeTable');
	var newTable = treeTable.cloneNode();
	var treeData = p.TreeTable;
	
	for(var i = 0; i < treeData.length; i++){
    var tr = document.createElement('tr');
    
		// Common name
		var td = document.createElement('td');
    td.appendChild(document.createTextNode(treeData[i][0]));
    tr.appendChild(td);
		
		// Color box
		var td = document.createElement('td');
		td.setAttribute("style", "background:" + treeData[i][3]);
		td.setAttribute("class", "colorCol");
    td.appendChild(document.createTextNode(" "));
    tr.appendChild(td);

		// Coverage pct
    var td = document.createElement('td');
    td.appendChild(document.createTextNode(treeData[i][1]));
    tr.appendChild(td);
		
		// Show and hide links
    var td = document.createElement('td');
		var shortname = treeData[i][2]
		
		var showLink = document.createElement('a');
		showLink.setAttribute("href", "#");
		showLink.setAttribute("id", "showLink" + shortname);
		showLink.appendChild(document.createTextNode('show'));							
		showLink.setAttribute('onclick', 'showTree("' + shortname + '")');
    td.appendChild(showLink);
		
		var hideLink = document.createElement('a');
		hideLink.setAttribute("href", "#");
		hideLink.setAttribute("id", "hideLink" + shortname);
		hideLink.appendChild(document.createTextNode('hide'));							
		hideLink.setAttribute('onclick', 'hideTree("' + shortname + '")');
    td.appendChild(hideLink);
		
    tr.appendChild(td);
		
		newTable.appendChild(tr);

	}
	treeTable.parentNode.replaceChild(newTable, treeTable);
	
	for(var i = 0; i < treeData.length; i++){
		document.getElementById("hideLink" + treeData[i][2]).style.display = 'none';
	}
	
}

function clearTable() {
	var treeTable = document.getElementById('treeTable');
	var newTable = document.createElement('table');
	newTable.setAttribute("id", "treeTable");
	treeTable.parentNode.replaceChild(newTable, treeTable);
}

// === Location Styles

function defaultStyle(feature) {
	return {
		selected: false, 
		weight: 1, opacity: 0.5, color: 'white', fillOpacity: 1, fillColor: feature.properties.Color
	};
}

function unselectedStyle() {
	return { 
		selected: false, 
		weight: 1, opacity: 0.5, color: 'white', fillOpacity: 1
	};
}

function selectedStyle() {
	return { 
		selected: true, 
		weight: 5, opacity: 1, color: '#862311', dashArray: '', fillOpacity: 1
	};
}

// === Location Layers and Events

var treeTableHeader = document.getElementById("treeTableHeader");
var lastSelected;

function selectFeature(e) {
	var layer = e.target;
	if (!layer.options.selected) {
		if (typeof lastSelected !== 'undefined') {
			lastSelected.setStyle(unselectedStyle());
		}
		layer.setStyle(selectedStyle());
		lastSelected = layer;

		if (!L.Browser.ie && !L.Browser.opera) { 
			layer.bringToFront(); 
		}
		
		treeTableHeader.innerHTML = layer.feature.properties.ShortDescription; 
		populateTable(layer.feature.properties);
		
	} else {
		geojson.resetStyle(e.target);
		layer.setStyle(unselectedStyle());
		treeTableHeader.innerHTML = 'Click on a region for a list of trees';
		clearTable();
	}
}

var locPrev = document.getElementById("locationPreview");
function onEachFeature(feature, layer) {
	layer.on({
		mouseover: function(e) {
			locPrev.innerHTML = e.target.feature.properties.Description;
		},
		mouseout: function(e) {
			locPrev.innerHTML = 'Hover over regions to show data'
		},
		click: selectFeature
	});
}

var geojson;
geojson = L.geoJson(locsData, {
	style: defaultStyle,
	onEachFeature: onEachFeature
}).addTo(map);

// === Tree Range Layers and Events

function showTree(shortname) {
	$.getScript("./data_trees/" + shortname + ".js")
		.done(function() {
			window["treeObj" + shortname] = L.geoJson(window["treeRange" + shortname], {
				style: { weight: 3, opacity: 0.5, color: 'green', fillOpacity: 0.5, fillColor: 'green' }
			});
			if (!map.hasLayer(window["treeObj" + shortname])) {
				map.addLayer(window["treeObj" + shortname]);				
			}
		});
	document.getElementById("showLink" + shortname).style.display = 'none';
	document.getElementById("hideLink" + shortname).style.display = 'inline';
}

function hideTree(shortname) {
	if (map.hasLayer(window["treeObj" + shortname])) {
		map.removeLayer(window["treeObj" + shortname]);
	}
	document.getElementById("showLink" + shortname).style.display = 'inline';
	document.getElementById("hideLink" + shortname).style.display = 'none';
}

// === Destroy map (for data reload)

function destroyMap() {
	map.remove();
	
	var oldMapDiv = document.getElementById("map");
	oldMapDiv.parentNode.removeChild(oldMapDiv);
	
	var newMapDiv = document.createElement("div");
	newMapDiv.setAttribute("id", "map");
	
	var mapContainer = document.getElementById('mapContainer');
	mapContainer.appendChild(newMapDiv);
}


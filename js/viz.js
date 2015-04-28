// === Initialize map with tile layer, legend, default view		

var map = L.map('map', { zoomControl: false }).setView([mapLat, mapLng], mapZoom);

L.tileLayer('https://{s}.tiles.mapbox.com/v3/{id}/{z}/{x}/{y}.png', {
	maxZoom: 12,
	attribution: '<a href="http://openstreetmap.org">OpenStreetMap</a> | <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a> | <a href="http://mapbox.com">Mapbox</a> | <a href="http://esp.cr.usgs.gov/data/little/">USGS</a>',
	id: 'examples.map-20v6611k'
}).addTo(map);

new L.Control.Zoom({ position: 'topleft' }).addTo(map);

function regionLink(linkText, region) {
	var aElem = document.createElement('a');
	aElem.setAttribute("href", "#");
	aElem.appendChild(document.createTextNode(linkText));
	aElem.setAttribute('onclick', 'loadRegion("' + region + '")');
	return aElem;
};

var legend = L.control({position: 'bottomleft'});
legend.onAdd = function (map) {
	var div = L.DomUtil.create('div', 'legend');
	div.innerHTML = '<b>Regional Maps</b> (click twice to load)<br/>';
	div.appendChild(document.createTextNode("State: "));	
	div.appendChild(regionLink('all', 'states'));
	div.appendChild(document.createElement('div'));

	div.appendChild(document.createTextNode("County: "));	
	div.appendChild(regionLink('all', 'counties'));
	div.appendChild(document.createTextNode(" "));	
	div.appendChild(regionLink('north-east', 'counties_ne'));	
	div.appendChild(document.createTextNode(" "));	
	div.appendChild(regionLink('mid-atl', 'counties_ma'));	
	div.appendChild(document.createTextNode(" "));	
	div.appendChild(regionLink('CA', 'counties_ca'));	
	div.appendChild(document.createTextNode(" "));	
	div.appendChild(regionLink('NY', 'counties_ny'));	
	div.appendChild(document.createTextNode(" "));	
	div.appendChild(document.createElement('div'));

	div.appendChild(document.createTextNode("Town: "));	
	div.appendChild(regionLink('CT', 'towns_ct'));
	div.appendChild(document.createTextNode(" "));	
	div.appendChild(regionLink('MA', 'towns_ma'));
	div.appendChild(document.createTextNode(" "));	
	div.appendChild(regionLink('ME', 'towns_me'));
	div.appendChild(document.createTextNode(" "));	
	div.appendChild(regionLink('NH', 'towns_nh'));
	div.appendChild(document.createTextNode(" "));	
	div.appendChild(regionLink('NY', 'towns_ny'));
	div.appendChild(document.createTextNode(" "));	
	div.appendChild(regionLink('RI', 'towns_ri'));
	div.appendChild(document.createTextNode(" "));	
	div.appendChild(regionLink('VT', 'towns_vt'));
	
	
//	var regions = ["states", "states_ne", "counties", "counties_ne", "counties_ca", "counties_ma", "counties_ne", "counties_ny", "towns_ct", "towns_ma", "towns_me", "towns_nh", "towns_ny", "towns_ri", "towns_vt"]
	
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


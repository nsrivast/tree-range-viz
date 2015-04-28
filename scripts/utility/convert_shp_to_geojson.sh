cd shapefiles

while read p; do
	cd $p
	ogr2ogr -f GeoJSON $p.geojson $p.shp	
	echo $p
	cd ..
done <../species_trunc.txt

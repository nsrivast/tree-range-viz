cd shapefiles

while read p; do
	curl -O http://esp.cr.usgs.gov/data/little/$p.zip
	echo $p
done <../species_trunc.txt

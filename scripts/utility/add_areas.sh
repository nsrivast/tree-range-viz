touch areas.txt

cd shapefiles
while read p; do
	echo $p,$(sed -n -e 's/^.*AREA": //p'  $p/$p.geojson | cut -d , -f 1 | awk '{s+=$1} END {print s}') >> ../areas.txt 
done <../species_trunc.txt

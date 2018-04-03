#!/bin/bash

# this script expects a Stack Overflow XML data file
# it will copy the xml header
# then copy entries from <beg> to <end>
# add the xml footer
# save to output.xml
#
# usage:
#	./slicer.sh <file> <beg> <end>

file=$1
beg=$2
end=$3

echo "file $file"
echo "beg $beg"
echo "end $end"

# add header for xml
head -2 $file > output.xml
# add sliced lines
head -$(($end+2)) $file | tail -$(($end-$beg)) >> output.xml
# add footer for xml
tail -1 $file >> output.xml

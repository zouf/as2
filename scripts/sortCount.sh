#!/bin/bash

mkdir -p sorted
echo "Looking for everything matching $1"
vars=`ls $1`
for i in $vars
do
  echo Sorting and counting: $i
  fname=sorted/$i.sorted
  sort $i >  tmp
  uniq -c tmp > tmp2
  sort -n -r tmp2 > tmp1
  awk '$2 != "Restaurants" && $2 != "" {print}' tmp1 > $fname
  rm tmp tmp2
done

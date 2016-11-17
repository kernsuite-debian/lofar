#!/bin/bash
#
#

files=(`find . -name "*.conf"`)

for file in "${files[@]}"
do
  newfile=$file".centos7"
  awk '{FS="[x[]"} {if ($0 ~ /\[/ && $0 !~ /^#/) {for (i=1;i<NF;i++) {val1 = $i - 1; printf "(0,"val1")"; if (i<NF-1) printf " x "; else printf " ["$NF"\n"}} else print $0}' $file > $newfile
done

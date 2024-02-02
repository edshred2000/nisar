#! /bin/bash

# h5_optimze.sh

# Description:
# Use 'h5repack' and 'h5stat' to cloud optimize a H5 file
# by implementing the HDF 'Page Aggregation' strategy
# for internal metadata aggregation.
#
# 'h5stat' determines the default Page size (usually 4096 bytes) and total cumaltive metadata size.
# 'h5repack' writes out a new file with a single aggregated cloud optized metadata Page size that a HDF reader 
# needs to read only once to access any HDF dataset or chunk within a dataset

# Usage:
# % h5_optimize <directory> <filename> || <file_regex>o
USAGE="Usage: h5_optimize.sh dir file"

if [ $# != 2 ] ; then
    echo $USAGE
    exit 1;
fi

dir=$1
file=$2
cd $dir

# get file exising metadata structure and sizes 
total_metadata_size=`h5stat $file | grep 'File metadata' | awk -F' ' '{print $3}'`
metadata_strategy=`h5stat $file | grep 'File space management strategy' | awk -F' ' '{print $5}'`
metadata_page_size=`h5stat $file | grep 'File space page size' | awk -F' ' '{print $5}'`

echo ""
echo " the HDF5 strategy is $metadata_strategy"
echo "  the metadata page size (bytes) is $metadata_page_size"
echo "   the total HDF5 internal metadata size (bytes) is $total_metadata_size"
echo ""


# cloud optimize if Page Aggregation is not turned on and default page size is 4096 bytes
if [ $metadata_strategy  == "H5F_FSPACE_STRATEGY_FSM_AGGR"  -a $metadata_page_size -eq 4096  ]; then

    # set the new page size based on ranges of powers of two
    if [ $total_metadata_size -gt 65536 -a $total_metadata_size -le 131072 ]; then
        new_metadata_page_size=131072
    elif [ $total_metadata_size -gt 131072 -a $total_metadata_size -le 262144 ]; then
        new_metadata_page_size=262144
    elif [ $total_metadata_size -gt 262144 -a $total_metadata_size -le 524288 ]; then
        new_metadata_page_size=524288
    elif [ $total_metadata_size -gt 524288 -a $total_metadata_size -le 1048576 ]; then
        new_metadata_page_size=1048576
    elif [ $total_metadata_size -gt 1048576 -a $total_metadata_size -le 2097152 ]; then
        new_metadata_page_size=2097152
    elif [ $total_metadata_size -gt 2097152 -a $total_metadata_size -le 4194304 ]; then
        new_metadata_page_size=4194304
    elif [ $total_metadata_size -gt 4194304 -a $total_metadata_size -le 8388608 ]; then
        new_metadata_page_size=8388608
    elif [ $total_metadata_size -gt 8388608 ]; then
        new_metadata_page_size=8388608
    fi

    echo " repacking using a page size of $new_metadata_page_size"
    echo " execute: % h5repack -S PAGE -G $new_metadata_page_size $file "repacked".$file"
    #`h5repack -S PAGE -G $new_metadata_page_size $file "repacked_page_to_$new_metadata_page_size".$file 2>&1   >/dev/null`
    `h5repack -S PAGE -G $new_metadata_page_size $file "repacked".$file 2>&1   >/dev/null`
    else
        echo “file cannot be optimized”
    fi

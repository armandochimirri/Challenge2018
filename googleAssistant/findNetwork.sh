#!/bin/bash

if [[ $# -ne 1 ]]; then
    echo "Wrong argument number"
    exit;
fi

interface=$1


ip=$(ifconfig ${interface} | grep "inet " | cut -f 10 -d " ");
netmask=$(ifconfig ${interface} | grep "inet " | cut -f 13 -d " ");

IFS=. read -r i1 i2 i3 i4 <<< ${ip}
IFS=. read -r m1 m2 m3 m4 <<< ${netmask}

printf "%d.%d.%d.%d %d.%d.%d.%d" "$((i1 & m1))" "$((i2 & m2))" "$((i3 & m3))" "$((i4 & m4))" $m1 $m2 $m3 $m4


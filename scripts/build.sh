#!/bin/bash

gcc html_to_csv.c -lz -I/usr/include/libxml2/ -lxml2 -o html_to_csv.out

#!/bin/sh
set -e
set -x

gcc -I $EMC2_HOME/include \
    -std=gnu99 \
    lui-test.c \
    -L $EMC2_HOME/lib -llinuxcnc-ui \
    -o lui-test

linuxcnc -r ./lui.ini


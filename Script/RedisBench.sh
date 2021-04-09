#!/bin/bash

for ((;;)) \
do \
    redis-benchmark  -p 6390  -n 1000000; \
    sleep 1000; \
done

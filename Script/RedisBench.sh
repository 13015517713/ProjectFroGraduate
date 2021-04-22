#!/bin/bash

ltime=100
rtime=1000
sleepTime=$[$RANDOM % ($rtime-$ltime) + $ltime]
for ((;;)) \
do \
    echo '----------- start to run. -----------------'
    taskset -c 39 redis-benchmark  -p 6390  -n 1000000; \
    echo '----------- start to sleep for '$sleepTime.'s --------------'
    sleep $sleepTime; \
done

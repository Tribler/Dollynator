#!/bin/bash

pid_file=plebnet/twistd_tribler.pid
pid=$(cat $pid_file)
kill -9 $pid
rm $pid_file
rm plebnet/twistd.log


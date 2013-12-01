#!/bin/bash

case "$1" in
  start)
    echo "Starting metis"
    # run application you want to start
    python metis.py /var/log/metis/server.log 2>&1 &
    ;;
  stop)
    echo "Stopping metis"
    # kill application you want to stop
    ps x | awk '/metis\.py/, NF=1' | xargs kill
    ;;
  *)
    echo "Usage: /etc/init.d/metis {start|stop}"
    exit 1
    ;;
esac

exit 0

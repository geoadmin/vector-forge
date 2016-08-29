#!/bin/bash
set -e
set -u

NUM=0
CPUS=$(grep "processor" < /proc/cpuinfo | wc -l)
QUEUE=""

# Functions
function echoqueue {
    for PID in $QUEUE
    do
        echo -n "$PID "
    done
}

function queue {
    QUEUE="$QUEUE
$1"
    NUM=$(($NUM+1))
    #echo -n "QUEUE ";echoqueue
}

function dequeue {
    OLDDEQUEUE=$QUEUE
    QUEUE=""
    for PID in $OLDDEQUEUE
    do
        if [ ! "$PID" = "$1" ] ; then
            QUEUE="$QUEUE
$PID"
        fi
    done
    NUM=$(($NUM-1))
    #echo -n "DEQUEUE ";echoqueue
}

function checkqueue {
    OLDCHQUEUE=$QUEUE
    for PID in $OLDCHQUEUE
    do
        if [ ! -d /proc/$PID ] ; then
            dequeue $PID
        fi
    done
}

build_topology() {
    try=1;sql="begin;SET work_mem='1GB';UPDATE karto.dkm10_bodenbedeckung SET the_geom_topo = toTopoGeom(the_geom, 'topology_karto_dkm10', 1 ) where  objectid = ${i};commit;";psql -c "${sql}" -d stopo_master &> /tmp/topo_insert_${i}.log && { echo "import success COMMIT ${i} with command ${sql}, try: ${try}" &> /tmp/topo_insert_${i}.log; return 0; }
    try=2;sql="begin;SET work_mem='1GB';UPDATE karto.dkm10_bodenbedeckung SET the_geom_topo = toTopoGeom(the_geom, 'topology_karto_dkm10', 1, 0.1 ) where  objectid = ${i};commit;";psql -c "${sql}" -d stopo_master &> /tmp/topo_insert_${i}.log && { echo "import success COMMIT ${i} with command ${sql}, try: ${try}" &> /tmp/topo_insert_${i}.log; return 0; }
    try=3;sql="begin;SET work_mem='1GB';UPDATE karto.dkm10_bodenbedeckung SET the_geom_topo = toTopoGeom(the_geom, 'topology_karto_dkm10', 1, 0.5 ) where  objectid = ${i};commit;";psql -c "${sql}" -d stopo_master &> /tmp/topo_insert_${i}.log && { echo "import success COMMIT ${i} with command ${sql}, try: ${try}" &> /tmp/topo_insert_${i}.log; return 0; }
    try=4;sql="begin;SET work_mem='1GB';UPDATE karto.dkm10_bodenbedeckung SET the_geom_topo = toTopoGeom(the_geom, 'topology_karto_dkm10', 1, 1.0 ) where  objectid = ${i};commit;";psql -c "${sql}" -d stopo_master &> /tmp/topo_insert_${i}.log && { echo "import success COMMIT ${i} with command ${sql}, try: ${try}" &> /tmp/topo_insert_${i}.log; return 0; }
    try=5;sql="begin;SET work_mem='1GB';UPDATE karto.dkm10_bodenbedeckung SET the_geom_topo = toTopoGeom(the_geom, 'topology_karto_dkm10', 1, 1.5 ) where  objectid = ${i};commit;";psql -c "${sql}" -d stopo_master &> /tmp/topo_insert_${i}.log && { echo "import success COMMIT ${i} with command ${sql}, try: ${try}" &> /tmp/topo_insert_${i}.log; return 0; }

    echo "ERROR import failed ${i} after ${try} try, last sql: ${sql}" &>> /tmp/topo_insert_${i}.log
}

for i in $(psql -qAt -c "select objectid from karto.dkm10_bodenbedeckung WHERE the_geom_topo IS NULL;" -d stopo_master)
do
    ( build_topology 1> /dev/null ) &
    PID=$!
    queue "$PID"
    echo "start processing $i with PID: $PID ..."
    # wait 0.2 seconds before starting the new image
    #sleep 0.2
    while [ $NUM -ge $CPUS ] # MAX PROCESSES
    do
        checkqueue
        #sleep 0.2
    done
done

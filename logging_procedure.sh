#!/usr/bin/env bash
log /home/s0816700/logging/whoson 3600 whoson -g &
log /home/s0816700/logging/gpu-usage 3600 gpu-usage -h &
log /home/s0816700/logging/gpu-usage-by-node 3600 gpu-usage-by-node &
log /home/s0816700/logging/cluster-status 3600 cluster-status &
log /home/s0816700/logging/user-usage 3600 make_logging_plots.py &
log /home/s0816700/logging/sprio 3600 sprio -l &
log /home/s0816700/logging/squeue 3600 squeue -r &
log /home/s0816700/logging/free-gpus 3600 free-gpus &
sleep infinity

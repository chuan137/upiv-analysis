#!/bin/bash

for alpha in 30 40 50 60 70 80 90 100 110 120; do
  for n in `echo {001..001}`; do
    ./simulate_ring.py -a `echo ${alpha}/100 | bc -l`
    mkdir -p figs/sim/$alpha
    mv figs/ring.tif figs/sim/ring_${alpha}_${n}.tif
    # mv figs/ring.png figs/sim/ring_${alpha}.png
  done
done

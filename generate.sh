#!/bin/bash

START=500
STEP=5
END=529

for i in $(seq $START $STEP $END); do
    echo $i
    CUDA_VISIBLE_DEVICES=0,1,2 $blender -b --engine CYCLES -P run.py -- --seed $i
done

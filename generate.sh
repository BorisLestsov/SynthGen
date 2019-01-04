#!/bin/bash

START=0
STEP=50
END=99999

for i in $(seq $START $STEP $END); do
    echo $i
    CUDA_VISIBLE_DEVICES=0,1,2 $blender -b --engine CYCLES -P run.py -- --seed $i
done

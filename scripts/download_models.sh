#!/bin/bash
set -e

MODEL_DIR="tmp/model/ssd_mobilenet_v2/1"
MODEL_URL="http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v2_coco_2018_03_29.tar.gz"

echo "Creating model directory..."
mkdir -p "$MODEL_DIR"

echo "Downloading model..."
curl -L -o tmp/model.tar.gz "$MODEL_URL"

echo "Extracting model..."
tar -xzvf tmp/model.tar.gz -C tmp/model

echo "Moving model files..."
mv tmp/model/ssd_mobilenet_v2_coco_2018_03_29/saved_model/saved_model.pb "$MODEL_DIR"

echo "Setting permissions..."
chmod -R 777 tmp/model

echo "Cleaning up..."
rm tmp/model.tar.gz
rm -rf tmp/model/ssd_mobilenet_v2_coco_2018_03_29

echo "Model ready at $MODEL_DIR"

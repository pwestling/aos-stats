#!/bin/bash
jekyll build
docker build -t gcr.io/oneoff-project/aosttsscrolls:latest .
docker push gcr.io/oneoff-project/aosttsscrolls:latest

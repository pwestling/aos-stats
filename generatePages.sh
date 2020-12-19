#!/usr/bin/env bash

find faction-indexes/*-dir/* | xargs -P 50 -I % python3 parsePage.py % aosttsscrolls/_posts

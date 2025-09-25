#!/usr/bin/env bash

while [ true ]; do
  venv/bin/python download_lasco.py
  venv/bin/python process_lasco.py

  venv/bin/python download_suvi.py
  venv/bin/python process_suvi_diffs.py
  venv/bin/python process_mlti_clr_suvi.py
  venv/bin/python process_histogram_analysis.py

  venv/bin/python process_movies.py
  
  venv/bin/python chs_main.py
  
  echo 'PAUSING for 1 hour...'
  sleep 1h
done

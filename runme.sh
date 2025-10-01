#!/usr/bin/env bash

#while [ true ]; do
  .venv/bin/python lasco.py

  .venv/bin/python download_suvi.py
  .venv/bin/python process_suvi_diffs.py
  .venv/bin/python process_mlti_clr_suvi.py
  .venv/bin/python process_histogram_analysis.py
  .venv/bin/python process_movies.py

#  python3 chs_main.py
  
#  echo 'PAUSING for 1 hour...'
#  sleep 1h
#done

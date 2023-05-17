#!/bin/bash
python extract_review_with_anns.py
python tag_pico.py
python calculate_pio_overlap.py

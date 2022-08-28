#!/bin/bash
python setup.py install
git add docs
git add bin
git add diary.md
git add emerge
git commit -m "Updates"
git push origin main

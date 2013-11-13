#!/usr/bin/sh

sudo python setup.py install
cd par_data
python run.py -i 'true'
python run.py
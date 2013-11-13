# usr/bin/sh

sudo rm -rf build
sudo rm -rf dist
sudo rm -rf par_data.egg-info
rm */*.pyc
rm */*/*.pyc
sudo python setup.py install
pythom -m python.run

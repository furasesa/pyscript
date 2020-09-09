#/bin/bash
echo "sync av_conv folder from pyscript"
rsync -avhP ~/storage/shared/Development/pyscript/av_conv ~/
echo "installing..."
python setup.py install
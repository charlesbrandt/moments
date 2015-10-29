#!/bin/bash

python /c/mindstream/mindstream/launch.py -c /c/moments moments

echo "
Other common options:
python /c/mindstream/mindstream/launch.py -c /c/moments todo
python /c/mindstream/mindstream/launch.py -c /c/moments tests
python /c/mindstream/mindstream/launch.py -c /c/moments server

python /c/mindstream/mindstream/launch.py -c /c/moments docs
python /c/mindstream/mindstream/launch.py -c /c/technical javascript
"

echo "new tab"
echo "cd /c/moments/moments"
echo "python server.py /c/moments/tests/"
echo ""

echo "new tab"
echo "cd /c/moments/tests"
echo "nosetests --exe"

#!/bin/bash

#may need to prefix launch.py if path is not set in .bashrc:
#python /c/mindstream/mindstream/

launch.py -c /c/public/moments moments

echo "
Other common options:
launch.py -c /c/public/moments todo
launch.py -c /c/public/moments tests
launch.py -c /c/public/moments server

launch.py -c /c/public/moments docs
launch.py -c /c/technical javascript
"

echo "FOR TESTING:"
echo "new tab"
echo "cd /c/public/moments/moments"
echo "python server.py /c/public/moments/tests/"
echo ""

echo "new tab"
echo "cd /c/public/moments/tests"
echo "nosetests --exe"

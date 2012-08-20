*2011
Deep Breath... Inhale.... Exhale.... :)

Greetings!
Welcome to Moments!

Moments is available at bitbucket.org/cbrandt/moments. 
Moments is free and open source software. 
Moments is released under the MIT license.  (See: LICENSE.txt)

This software was made possible by the love of TCB, my family, my teachers and my friends.  
Thank you!

Have fun. Be happy. Be free. Namaste.

SUMMARY:
----------
Moments is a python package to process moments log files. 
Moment log files are simple text documents with the format: 
        *YYYY.MM.DD hh:mm [tags]
        [entry]
        \n

        This simple format allows your notes to:
	  -stay accessible (no proprietary formats)
	  -be sorted by time or tag
	  -easily synchronize across many machines using a distributed version control system

REQUIREMENTS:
----------------
Make sure you have the following items available on your computer:

Python: (currently using versions 2.5 and up)
http://www.python.org

Image manipulations are an optional part of the path.py module and require:
Python Image Library (or Pillow)
jhead command line utility

Higher level notes for installing and configuring a computer system that runs python are beyond the scope of this document.  For details and recommendations on this process, please see:
charlesbrandt.com

GETTING STARTED:	
-------------------
easy_install moments

or, if you've downloaded a source distribution:
python setup.py install 

CONTACT:
-------------
You may be able to reach me via code [at] contextiskey [dot] com.  


DOCS:
---------
Complete documentation can be found in:
docs/

To generate the documentation, you will need Sphinx:
sudo easy_install sphinx

cd docs/
sphinx-build -b html . ./_build


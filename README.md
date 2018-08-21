Moments
========

Moments is a Python library that helps parse text based notes.  These notes are easy to create in a text editor, easy to read by a human and easy to parse with a computer.  These properties make it easy to sort and organize notes, and customize the sort process using this library.

This project was started before Evernote and mobile apps emerged to help with keeping a personal journal.  Although this is a much lower level approach (and not as user friendly), I still use it as my primary means of keeping notes.

EDITORS
-------------
Just like with editing python, it helps to have the right editor so that you can work fluidly.

There are a lot of good ones that I've used, including:

  - [Atom](editors/atom.md)
  - [Emacs](editors/emacs/emacs.md)
  - [vi](editors/vi/vi.md)

DOCS
---------

Full documentation is available here:

http://pythonhosted.org/Moments/

The documentation is generated from sources found in the 'docs/' directory. To generate the documentation, you will need Sphinx:

   sudo easy_install sphinx

then:

   cd docs/
   sphinx-build -b html . ./_build

or:

   make html

INSTALL:
----------

see docs/installation.txt

and

docs/_build/html/installation.html


TEST:
----------

cd /path/to/moments/moments
python server.py /path/to/moments/tests/

#new tab:
cd tests/
nosetests

ETC:
-------------

Moments is available at bitbucket.org/cbrandt/moments.
Moments is free and open source software.
Moments is released under the MIT license.  (See: LICENSE.txt)

This software was made possible by the love of TCB, my family, my teachers and my friends.  
Thank you!

Have fun. Be happy. Be free.


### From technical documentation / charlesbrandt.com

If you haven't done this as part of your system install, or if you're forging on with a simple system, install the python moments module:

easy_install moments

or if you don't have easy_install,
python/downloads/ez_setup.py

or just download the package:

and install from there:
python setup.py install
or
python setup.py develop

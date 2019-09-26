# Moments

Moments is a Python library for parsing text based journals. The format is easy to create in a text editor, easy to read by a human and easy to parse with a computer. These features make it easier to sort and organize notes using this library.

This project was started before Evernote and mobile apps emerged to help with keeping a personal journal.  Although this is a much lower level approach (and not as user friendly), I still use it as my primary means of keeping notes.

## Making moments
 
It helps to have the right text editor so that you can write fluidly. The main requirement is creating a timestamp with minimal effort.

There are a lot of good editors that allow customization with modules, plugins or packages. Here are a few that assist with creating timestamps:

  - [Atom](editors/atom.md)
  - [Emacs](editors/emacs/emacs.md)
  - [vi](editors/vi/vi.md)

## Docs

Full documentation is available here:

http://pythonhosted.org/Moments/

The documentation is generated from sources found in the 'docs/' directory. To generate the documentation, you will need Sphinx:

   sudo easy_install sphinx

then:

   cd docs/
   sphinx-build -b html . ./_build

or:

   make html

## Install

see docs/installation.txt

and

docs/_build/html/installation.html


## Test

cd /path/to/moments/moments
python server.py /path/to/moments/tests/

#new tab:
cd tests/
nosetests

## Etc

Moments is available at github.com/charlesbrandt/moments.
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

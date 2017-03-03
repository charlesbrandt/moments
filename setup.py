"""
To install moments in 'develop' mode, you can use pip:
	
    pip3 install -e .

This assumes pip is available. If not, run python3 get-pip.py
 
via:
http://stackoverflow.com/questions/2087148/can-i-use-pip-instead-of-easy-install-for-python-setup-py-install-dependen

This is a nice guide for writing setup.py files... thanks!
http://www.diveintopython3.net/packaging.html
"""
from distutils.core import setup

version = '3.0'

setup(
    name='moments',
    version=version,
    description="Process notes and journals stored as moments log files",
    long_description="""Moment log files are simple text documents with the format:
        
        *YYYY.MM.DD hh:mm [tags]
        [entry]
        \n

        This simple format allows your notes to:
	  -stay accessible (no proprietary formats)
	  -be sorted by time or tag
	  -easily synchronize across many machines using a distributed version control system
    """,
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Topic :: Text Processing :: Markup",
        "Topic :: Text Editors :: Text Processing"
        ],
    keywords='moments journal log self_tracking logging blog entry time quantified_self evernote emacs time time_management history mind_map mental_map',
    author='Charles Brandt',
    author_email='code@charlesbrandt.com',
    #url='http://bitbucket.org/cbrandt/moments',
    url='http://github.com/charlesbrandt/moments',
    license='MIT',
)

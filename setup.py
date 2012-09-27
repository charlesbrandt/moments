try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import sys, os

version = '2.0'

setup(
    name='Moments',
    version=version,
    description="Python package to process moments log files",
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
    classifiers=[],
    keywords='moments journal log self_tracking logging blog entry time quantified_self evernote emacs time time_management history',
    author='Charles Brandt',
    author_email='code@charlesbrandt.com',
    url='http://bitbucket.org/cbrandt/moments',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
      'setuptools',
    ],
    entry_points="""
    """,
)

from setuptools import setup, find_packages
import sys, os

version = '1.0'

setup(name='osbrowser',
      version=version,
      description="OSBrowser provides a high level interface to local filesystems",
      long_description="""\
OSBrowser is a python module that provides an object oriented interface to your computer's local filesystem.  It leverages python's native os and os.path libraries to give an object oriented interface to the system.  Starting at the level of Nodes on a filesystem, it works up to higher level objects such as Images and Playlists. 

I like to think of it as a python based file system explorer/browser/finder without a graphical user interface.

OSBrowser can utilize the Moments module for logging and meta data generation.  This ensures metadata will not get locked into proprietary formats. 
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='os browser filesystem interface images sounds playlists lists nodes files',
      author='Charles Brandt',
      author_email='code@contextiskey.com',
      url='http://www.contextiskey.com',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )

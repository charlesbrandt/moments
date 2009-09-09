from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='converter',
      version=version,
      description="A collection of scripts to assist in converting playlists found in one format to another.  SAlso see the medialist module.",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='playlists medialists conversion converter playlist medialist',
      author='Charles Brandt',
      author_email='code@contextiskey.com',
      url='http://contextiskey.com',
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

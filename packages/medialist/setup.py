from setuptools import setup, find_packages
import sys, os

version = '1.0'

setup(name='medialist',
      version=version,
      description="List like object to add playlist methods.  Based on media paths, but can also store osbrowser objects to rerepresent files",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='playlist medialist',
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

from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='launcher',
      version=version,
      description="A collection of functions to assist in launching applications from python using the python subprocess module",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='launcher subprocess desktop operating_system configuration',
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

from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(name='quotes',
      version=version,
      description="Provides access to a list of quotes in a text file",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='yoga sutras patanjali quotes',
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

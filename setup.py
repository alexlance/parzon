""" Wrapper to enable executable entrypoint for program. """
from setuptools import setup

setup(name='parzon', version='0.7', packages=['parzon'],
      entry_points={'console_scripts': ['parzon = parzon.__main__:main']})

#!/usr/bin/env python3

from setuptools import setup, find_packages
import pulseviz


setup(
    name='pulseviz',
    version=pulseviz.__version__,
    author='Patrick Bartels',
    author_email='pckbls@gmail.com',
    description='Audio visualizer for PulseAudio written in Python',
    url='https://github.com/pckbls/pulseviz',
    license='MIT',
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=[
        'pyglet',
        'numpy'
    ],
    entry_points={
        'console_scripts': [
            'pulseviz = pulseviz.main:main'
        ]
    }
)

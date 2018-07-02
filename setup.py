#!/usr/bin/env python3

import setuptools

with open('README.md', 'r') as fh:
    long_discription = fh.read()

setuptools.setup(
    name='wecli',
    version='0.1.2',
    author='Tin Unkai',
    author_email='tinunkai@gmail.com',
    description='A wechat client in terminal.',
    long_discription=long_discription,
    long_discription_content_type='text/markdown',
    url='https://github.com/tinunkai/WeCli',
    packages=setuptools.find_packages(),
    classifiers=(
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ),
)


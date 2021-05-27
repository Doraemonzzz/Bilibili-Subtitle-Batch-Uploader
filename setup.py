# coding: utf-8

from distutils.core import setup

setup(
    name='bisbu',
    version='0.0.1',
    description='Bilibili subtitle batch uploader',
    author='Doraemonzzz',
    author_email='doraemon_zzz@163.com',
    url='https://github.com/agermanidis/autosub',
    packages=['bisbu'],
    entry_points={
        'console_scripts': [
            'bisbu = bisbu:main',
        ],
    },
    install_requires=[
        'pysrt>=1.0.1',
        'pyvtt>=0.0.1',
        'tqdm>=4.61.0',
    ],
)
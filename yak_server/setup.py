# pylint: disable=C0330
import os.path

import setuptools

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
README_PATH = os.path.join(ROOT_DIR, 'README.rst')

with open(README_PATH, encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setuptools.setup(
    name='yak_server',
    version='0.1',
    description='Server for yak home automation system.',
    long_description=LONG_DESCRIPTION,

    url='https://github.com/snah/yak_server',

    author='Hans Maree',
    author_email='hans.maree@gmail.com',

    license='GNU General Public License v3.0',

    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'Programming Language :: Python :: 3',
                 'Topic :: Home Automation'
                 ],

    keywords='',

    packages=['yak_server'],
)

# codinf: utf-8

from distutils.core import setup


setup(
    name='netlog',
    version='0.1',
    py_modules=['netlog'],
    url='https://github.com/lemanyk/netlog',
    description='logging stream server written on gevent',
    author='Gennady Leman',
    author_email='lemanyk@gmail.com',
    install_requires=['gevent'],
)

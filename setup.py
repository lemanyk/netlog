# codinf: utf-8

from distutils.core import setup


setup(
    name='netlog',
    version='0.2',
    py_modules=['netlog'],
    url='https://github.com/lemanyk/netlog',
    download_url='https://github.com/lemanyk/netlog/',
    description='logging stream server written on gevent',
    author='Gennady Leman',
    author_email='lemanyk@gmail.com',
    install_requires=['gevent'],
    license='MIT',
    classifiers=[
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'Operating System :: POSIX',
          'Programming Language :: Python',
    ],
)

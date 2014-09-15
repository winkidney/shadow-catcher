import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'sqlalchemy',
    'pyquery',
    'celery',
    'redis',
    'eventlet',
    'greenlet',
    'requests',
    ]

setup(name='shadow-catcher',
      version='0.1',
      description='simple spider framework with threads support',
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: urllib :: Application",
        ],
      author='winkidney',
      author_email='winkidney@gmail.com',
      url='http://github.com/winkidney/shadow-catcher.git',
      keywords='spider urllib framework',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      #test_suite="",
      )

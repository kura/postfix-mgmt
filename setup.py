import os
import sys
from setuptools import setup
from setuptools import find_packages
from postfixmgmt import __version__


setup(name='postfixmgmt',
      version=__version__,
      url='http://postfixmgmt.syslog.so/',
      author="Kura",
      author_email="kura@kura.io",
      description="SQL-based management system for Postfix",
      long_description = file(
          os.path.join(
              os.path.dirname(__file__),
              'README.rst'
          )
      ).read(),
      license='BSD',
      platforms=['linux'],
      packages=['postfixmgmt',],
      install_requires=[
            'Flask==0.8',
            'Jinja2==2.6',
            'py-bcrypt==0.2',
            'SQLAlchemy==0.7.5',
            'Flask_SQLAlchemy==0.15',
            'Flask_WTF==0.5.2',
          ],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Utilities',
        'Topic :: Internet :: WWW/HTTP',
    ],
)

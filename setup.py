import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'geoalchemy2',
    'psycopg2',
    'pyflakes',
    'pyramid',
    'pyramid_mako',
    'pyramid_debugtoolbar',
    'regex',
    'SQLAlchemy',
    'waitress',
    ]

setup(name='vector-forge',
      version='0.0',
      description='vector-forge',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="vectorforge",
      entry_points="""\
      [paste.app_factory]
      main = vectorforge:main
      """,
      )

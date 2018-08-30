
from setuptools import setup
setup(**{'author': 'turtle',
 'author_email': 'foo@gmail.com',
 'classifiers': ['Development Status :: 5 - Production/Stable',
                 'Environment :: Web Environment',
                 'Intended Audience :: Developers',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Topic :: Internet :: WWW/HTTP'],
 'description': '...',
 'include_package_data': True,
 'install_requires': ['pytest<4,>=3.6.3',
                      'requests<3,>=2.19.1',
                      'splinter<1,>=0.8.0',
                      'orcid<2,>=1.0.2',
                      'pkgversion<4,>=3.0.2'],
 'long_description': '$ pytest tests/orcid -s --env prod',
 'name': 'service-de-auth',
 'packages': ['config',
              'test_utils',
              'tests',
              'services',
              'tests.orcid',
              'services.orcid',
              'services.flower',
              'services.base'],
 'tests_require': ['tox'],
 'url': 'https://github.com/turtle321/feature-tests-turtle-inspire',
 'version': None,
 'zip_safe': False})
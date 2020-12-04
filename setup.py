from setuptools import setup, find_packages

version = '1.0.2'

requires = [
    'setuptools',
    'openprocurement.api>=2.4',
    'openprocurement.audit.api>=1.0.9',
    'openprocurement.tender.core>=2.4',
    'restkit>=0.27.2'
]
test_requires = requires + [
    'webtest',
    'freezegun',
    'python-coveralls',
]
docs_requires = requires + [
    'sphinxcontrib-httpdomain',
]

entry_points = {
    'openprocurement.api.plugins': [
        'audit.inspection = openprocurement.audit.inspection:includeme'
    ]
}

setup(name='openprocurement.audit.inspection',
      version=version,
      description="",
      long_description=open("README.md").read(),
      classifiers=[
        "Programming Language :: Python",
      ],
      keywords='',
      author='RaccoonGang',
      author_email='info@raccoongang.com',
      license='Apache License 2.0',
      url='https://github.com/ProzorroUKR/openprocurement.audit.inspection',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['openprocurement', 'openprocurement.audit'],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=test_requires,
      extras_require={'test': test_requires, 'docs': docs_requires},
      test_suite="openprocurement.audit.inspection.tests.main.suite",
      entry_points=entry_points,
      )

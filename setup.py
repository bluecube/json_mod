from setuptools import setup

with open("Readme") as fp:
    readme = fp.read()

setup(name = 'json_mod',
      version = '1.0.0',
      description = 'Parser of a JSON-based language intended for configuration files.',
      long_description = readme,
      url = 'https://github.com/bluecube/json_mod',
      author = 'Kuba Marek',
      author_email = 'blue.cube@seznam.cz',
      license = 'MIT',
      packages = ['json_mod'],
      zip_safe = True,
      test_suite = 'nose.collector',
      tests_require = ['nose'])


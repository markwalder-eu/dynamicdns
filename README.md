
[![codecov](https://codecov.io/gh/amarkwalder/dynamicdns/branch/master/graph/badge.svg)](https://codecov.io/gh/amarkwalder/dynamicdns)

# CI Build
- coverage run --source dynamicdns --branch --omit "*/__init__.py" -m unittest discover
- coverage html
- coverage report -m
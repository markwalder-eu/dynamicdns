
[![TravisCI](https://travis-ci.org/amarkwalder/dynamicdns.svg)](https://travis-ci.org/amarkwalder/dynamicdns)
[![codecov](https://codecov.io/gh/amarkwalder/dynamicdns/branch/master/graph/badge.svg)](https://codecov.io/gh/amarkwalder/dynamicdns)

# Installation
## Prerequisites
- Install Node.js
- Install Python
    - Python Virtual Environment
- Install serverless

## Prepare configuration
- Copy config files to config directory



# CI Build
- coverage run --source dynamicdns --branch --omit "*/\_\_init\_\_.py" -m unittest discover
- coverage html
- coverage report -m

# Execute Client
- bash <(curl -sSL https://api-dev.markwalder.eu/dynamicdns-v1/script) -c config/client.config.example

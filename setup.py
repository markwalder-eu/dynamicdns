from setuptools import setup
import dynamicdns

setup(
    name            = 'dynamicdns',
    use_scm_version = True,
    setup_requires  = [ 'setuptools_scm' ],
    author          = dynamicdns.__author__,
    author_email    = dynamicdns.__author_email__  
)
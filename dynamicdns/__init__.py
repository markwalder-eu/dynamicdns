
def version():
    """Extract version in file.  Returns version string"""
    try:
        with open("dynamicdns/version") as file:  
            return file.read() 
    except:
        return "[Version will be generated during deployment]"

__author__ = "André Markwalder"
__author_email__ = "andre.markwalder@gmail.com"
__version__ = version()

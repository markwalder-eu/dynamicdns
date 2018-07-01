import boto3


class Boto3Wrapper(object):
    
    _CLIENT_CACHE = {}
    CLIENT_CREATION_HOOK = None

    @classmethod
    def get_client(cls, *args, **kwargs):
        key = tuple(sorted(kwargs.items()))
        if key in cls._CLIENT_CACHE:
            return cls._CLIENT_CACHE[key]
        client = boto3.client(*args, **kwargs)
        if cls.CLIENT_CREATION_HOOK and callable(cls.CLIENT_CREATION_HOOK):
            client = cls.CLIENT_CREATION_HOOK.__get__(client)
        cls._CLIENT_CACHE[key] = client
        return client



class Error:
    def __init__(self, msg: str):
        self.msg = msg
 
    def __str__(self):
        return str(self.msg)


class ConfigProvider:

    def load(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def shared_secret(self, hostname: str):
        raise NotImplementedError("Subclass must implement abstract method")

class DNSProvider:

    def read(self, hostname: str):
        raise NotImplementedError("Subclass must implement abstract method")

    def update(self, hostname: str, updateip: str):
        raise NotImplementedError("Subclass must implement abstract method")

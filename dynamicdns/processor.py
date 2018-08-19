import re
import hashlib

from dynamicdns.models import Error, ConfigProvider, DNSProvider


def factory(dns: DNSProvider):
    return Processor(dns)


class Processor:

    def __init__(self, dns: DNSProvider):
        self.dns = dns

    def checkhash(self, hostname: str, validationhash: str, sourceip: str, sharedsecret: str):

        error = self.__checkhashformat(validationhash)
        if isinstance(error, Error):
            return error

        error = self.__comparehash(sourceip, hostname, sharedsecret, validationhash)
        if isinstance(error, Error):
            return error

    def update(self, hostname: str, sourceip: str, internalip: str):

        updateip = sourceip
        if internalip != "":
            updateip = internalip

        currentip = error = self.dns.read(hostname)
        if isinstance(error, Error):
            return error

        if currentip == updateip:
            return "Your IP '" + currentip + "' address matches the current DNS record for '" + hostname + "'."

        updateip = error = self.dns.update(hostname, updateip)
        if isinstance(error, Error):
            return error

        return "Your hostname record '" + hostname + "' has been updated from '" + currentip + "' to '" + updateip + "'."


    def __checkhashformat(self, validationhash: str):
        if not re.match(r'[0-9a-fA-F]{64}', validationhash):
            return Error("You must pass a valid sha256 hash in the hash= querystring parameter.")


    def __comparehash(self, sourceip: str, hostname: str, sharedsecret: str, validationhash: str):
        hashinput: str = sourceip + hostname + sharedsecret
        calculatedhash: str = hashlib.sha256(hashinput.encode('utf-8')).hexdigest()
        if not calculatedhash == validationhash:
            return Error("Validation of hashes failed.")


#!/usr/bin/env python3
#coding:utf8

import socket
import sys

# libpath

try:
    if (sys.version_info.major != 3) or (sys.version_info.minor < 4):
        raise Exception("You must run Syncplay with Python 3.4 or newer!")
except AttributeError:
    import warnings
    warnings.warn("You must run Syncplay with Python 3.4 or newer!")

from OpenSSL import crypto
from twisted.internet import reactor, ssl
from twisted.internet.endpoints import SSL4ServerEndpoint

from syncplay.server import SyncFactory, ConfigurationGetter

tlsCertPath = 'cert'
privkey = open(tlsCertPath+'/privkey.pem', 'rt').read()
certif = open(tlsCertPath+'/cert.pem', 'rt').read()
chain = open(tlsCertPath+'/chain.pem', 'rt').read()

privkeypyssl = crypto.load_privatekey(crypto.FILETYPE_PEM, privkey)
certifpyssl = crypto.load_certificate(crypto.FILETYPE_PEM, certif)
chainpyssl = [crypto.load_certificate(crypto.FILETYPE_PEM, chain)]

cipherListString = "ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:"\
                   "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:"\
                   "ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384"
accCiphers = ssl.AcceptableCiphers.fromOpenSSLCipherString(cipherListString)

contextFactory = ssl.CertificateOptions(privateKey=privkeypyssl, certificate=certifpyssl,
                                        extraCertChain=chainpyssl, acceptableCiphers=accCiphers,
                                        raiseMinimumTo=ssl.TLSVersion.TLSv1_2)

if __name__ == '__main__':
    argsGetter = ConfigurationGetter()
    args = argsGetter.getConfiguration()
    factory = SyncFactory(
        args.port,
        args.password,
        args.motd_file,
        args.isolate_rooms,
        args.salt,
        args.disable_ready,
        args.disable_chat,
        args.max_chat_message_length,
        args.max_username_length,
        args.stats_db_file
    )
    endpoint4 = SSL4ServerEndpoint(reactor, int(args.port), contextFactory, interface='0.0.0.0')
    endpoint4.listen(factory)
    endpoint6 = SSL4ServerEndpoint(reactor, int(args.port), contextFactory, interface='::')
    endpoint6.listen(factory)
    reactor.run()

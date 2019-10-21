# -*- coding: utf-8 -*-
""" Util function to convert .pfx and .pkcs12 certs to key+cert+chain for
use in Python sockets"""
import tempfile
import OpenSSL.crypto


def pfx_to_pem(path=None, password=None):
    """
    Decrypts the .pfx file to be used with requests.
    :param path: path to .pfx/.pkcs12 file
    :param password: password of certificate
    :return: NamedTemporaryFile temp_key, temp_cert, temp_ca paths
    """
    temp_key = tempfile.NamedTemporaryFile(suffix='.key')
    temp_cert = tempfile.NamedTemporaryFile(suffix='.crt')
    temp_ca = tempfile.NamedTemporaryFile(suffix='.crt')

    f_key = open(temp_key.name, 'wb')
    f_cert = open(temp_cert.name, 'wb')
    f_ca = open(temp_ca.name, 'wb')

    pfx = open(path, 'rb').read()
    p12 = OpenSSL.crypto.load_pkcs12(pfx, password)

    f_key.write(OpenSSL.crypto.dump_privatekey(
        OpenSSL.crypto.FILETYPE_PEM, p12.get_privatekey()))
    f_cert.write(OpenSSL.crypto.dump_certificate(
        OpenSSL.crypto.FILETYPE_PEM, p12.get_certificate()))
    ca = p12.get_ca_certificates()
    if ca is not None:
        for cert in ca:
            f_ca.write(OpenSSL.crypto.dump_certificate(
                OpenSSL.crypto.FILETYPE_PEM, cert))
    f_key.close()
    f_cert.close()
    f_ca.close()
    return temp_key, temp_cert, temp_ca

import requests
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()
from requests.packages.urllib3.util.ssl_ import create_urllib3_context

from util import second_way_to_load, first_way_to_load


EC_CERT = """<FILL IN>"""


def test_load_key_generic(cert, key):
    """
        Args:
            cert: file path, can be either PEM or DER file, e.g. b"./cert.pem"
            key: file path or key object
    """
    context = create_urllib3_context()
    ctx = context._ctx._context

    from OpenSSL import crypto
    from OpenSSL._util import lib as _lib
    import certifi
    from OpenSSL._util import exception_from_error_queue as _exception_from_error_queue

    # Load certificate with the given file path
    file_type = 2 if b"der" in cert else 1
    if not _lib.SSL_CTX_use_certificate_file(ctx, cert, file_type):
        print("using cert")
        _exception_from_error_queue(Exception)
    
    # Load the private key. It can be a file path, or a key object.
    if isinstance(key, bytes):
        # key is a file path
        print("key is a file path")
        file_type = 2 if b"der" in key else 1
        if not _lib.SSL_CTX_use_PrivateKey_file(ctx, key, file_type):
            _exception_from_error_queue(Exception)
    else:
        # key is an object
        print("key is an object")
        if not _lib.SSL_CTX_use_PrivateKey(ctx, key):
            _exception_from_error_queue(Exception)
    print("succeeded")

def test_load_ec_key(key):
    """
        Args:
            key: file path (can be either PEM or DER file) or key object
    """
    context = create_urllib3_context()
    ctx = context._ctx._context

    from OpenSSL import crypto
    from OpenSSL._util import lib as _lib
    import certifi
    from OpenSSL._util import exception_from_error_queue as _exception_from_error_queue

    x509 = crypto.load_certificate(crypto.FILETYPE_PEM, EC_CERT)
    context.load_verify_locations(cafile=certifi.where())
    context._ctx.use_certificate(x509)
    
    if isinstance(key, bytes):
        # key is a file path
        print("key is a file path")
        file_type = 2 if b"der" in key else 1
        if not _lib.SSL_CTX_use_PrivateKey_file(ctx, key, file_type):
            _exception_from_error_queue(Exception)
    else:
        # key is an object
        print("key is an object")
        if not _lib.SSL_CTX_use_PrivateKey(ctx, key):
            _exception_from_error_queue(Exception)
    print("succeeded")


if __name__ == "__main__":
    #test_load_key_generic(b"./cert.pem", b"./key.pem")
    #test_load_key_generic(b"./cert.pem", first_way_to_load(b"pkcs11:token=token1;object=mtlskey;pin-value=mynewpin"))
    #test_load_ec_key(first_way_to_load(b"pkcs11:token=token1;object=mtlskey;pin-value=mynewpin"))
    pass
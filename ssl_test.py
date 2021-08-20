def test_use_key_from_file(cert_path, key_path):
    import OpenSSL.SSL
    from OpenSSL._util import lib as _lib
    from OpenSSL._util import exception_from_error_queue as _exception_from_error_queue
    
    context = OpenSSL.SSL.Context(6)

    if not _lib.SSL_CTX_use_certificate_file(context._context, cert_path, 1):
        _exception_from_error_queue(Exception)
    if not _lib.SSL_CTX_use_PrivateKey_file(context._context, key_path, 1):
        _exception_from_error_queue(Exception)
    if not _lib.SSL_CTX_check_private_key(context._context):
        print("check private key failed")
    print("test_use_key_from_file succeeded")

def test_use_key_from_hsm(cert_path, key_id):
    import OpenSSL.SSL
    from OpenSSL._util import exception_from_error_queue as _exception_from_error_queue
    from OpenSSL._util import (
        ffi as _ffi,
        lib as _lib,
    )

    null = _ffi.NULL

    _lib.ENGINE_load_builtin_engines()
    e = _lib.ENGINE_by_id(b"dynamic")
    if not e:
        raise ValueError("failed to load engine")
    if not _lib.ENGINE_ctrl_cmd_string(e, b"ID", b"pkcs11", 0):
        raise ValueError("failed to set ID")
    if not _lib.ENGINE_ctrl_cmd_string(e, b"SO_PATH", b"/usr/lib/x86_64-linux-gnu/engines-1.1/libpkcs11.so", 0):
        raise ValueError("failed to set dynamic_path")
    if not _lib.ENGINE_ctrl_cmd_string(e, b"LOAD", null, 0):
        raise ValueError("cannot LOAD")
    if not _lib.ENGINE_ctrl_cmd_string(e, b"MODULE_PATH", b"/usr/local/lib/softhsm/libsofthsm2.so", 0):
        raise ValueError("failed to set MODULE_PATH")
    if not _lib.ENGINE_init(e):
        raise ValueError("failed to init engine: ")

    key = _lib.ENGINE_load_private_key(e, key_id, null, null)
    if not key:
        raise ValueError("failed to load private key: ")
    
    context = OpenSSL.SSL.Context(6)

    if not _lib.SSL_CTX_use_certificate_file(context._context, cert_path, 1):
        _exception_from_error_queue(Exception)
    if not _lib.SSL_CTX_use_PrivateKey(context._context, key):
        _exception_from_error_queue(Exception)
    print("test_use_key_from_hsm succeeded")

if __name__ == "__main__":
    print("============ testing using key from file ================")
    test_use_key_from_file(b"./cert.pem", b"./key.pem")
    print("============ testing using key from hsm ================")
    test_use_key_from_hsm(b"./cert.pem", b"pkcs11:token=token1;object=mtlskey;pin-value=mynewpin")


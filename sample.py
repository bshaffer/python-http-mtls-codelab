from google.auth.transport.requests import AuthorizedSession
import google.auth
from google.auth.transport import mtls

credentials, _ = google.auth.default()

cert = b"""<fill_in_PEM_cert>"""

key = b"""<fill_in_PEM_private_key>"""

key_info = {
    "engine_id": b"pkcs11",
    "pin": b"mynewpin",
    "key_id": b"1111",
    "so_path": b"/usr/lib/x86_64-linux-gnu/engines-1.1/pkcs11.so",
    "module_path": b"/usr/local/lib/softhsm/libsofthsm2.so"
}

project = "sijunliu-dca-test"

def my_cert_callback():
    return cert, key

def my_cert_callback_hsm():
    return cert, key_info

def run_sample(client_cert_callback):
    authed_session = AuthorizedSession(credentials)
    authed_session.configure_mtls_channel(client_cert_callback=my_cert_callback)

    response = authed_session.request('GET', f'https://pubsub.mtls.googleapis.com/v1/projects/{project}/topics')
    print(response.text)


run_sample(my_cert_callback)
run_sample(my_cert_callback_hsm)
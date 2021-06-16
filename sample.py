from google.auth.transport.requests import AuthorizedSession
import google.auth
from google.auth.transport import mtls

credentials, _ = google.auth.default()

cert = b"""<fill_in_PEM_cert>"""

key = b"""<fill_in_PEM_private_key>"""

hsm_key = b"engine:pkcs11:1111:mynewpin"

project = "sijunliu-dca-test"

def my_cert_callback():
    return cert, key

def my_cert_callback_hsm():
    return cert, hsm_key

def run_sample(client_cert_callback):
    authed_session = AuthorizedSession(credentials)
    authed_session.configure_mtls_channel(client_cert_callback=my_cert_callback)

    response = authed_session.request('GET', f'https://pubsub.mtls.googleapis.com/v1/projects/{project}/topics')
    print(response.text)


run_sample(my_cert_callback)
run_sample(my_cert_callback_hsm)
# PKCS11 Codelab using google-auth-library-python

This is a codelab that demonstrates the sample use case of using google-auth-library-python with mTLS authentication where the certificate is loaded with PKCS11 interface. This codelab is for HTTP transport using requests library only.

### Pre-requisite

- This codelab is supposed to be ran at Debian GNU/Linux.
- Your environment should have Python 3 installed.

### Download the codelab and its dependencies

```bash
# Clone the codelab repo
git clone https://github.com/arithmetic1728/python-http-mtls-codelab.git

cd python-http-mtls-codelab.git

# Create and activate a Python virtual environment
pyenv virtualenv my_env
pyenv local my_env

# Install the dependencies.
python -m pip install pyopenssl
python -m pip install git+https://github.com/googleapis/google-auth-library-python.git@corp_cert
```

## Install PKCS11 support and Verify with OpenSSL

### Install openssl with pkcs11 

First install openssl with its [PKCS11 engine](https://github.com/OpenSC/libp11#openssl-engines).

```bash
# add to /etc/apt/sources.list
  deb http://http.us.debian.org/debian/ testing non-free contrib main

# then
$ export DEBIAN_FRONTEND=noninteractive 
$ apt-get update && apt-get install libtpm2-pkcs11-1 tpm2-tools libengine-pkcs11-openssl opensc -y
```

Note, the installation above adds in the libraries for all modules in this repo (TPM, OpenSC, etc)..you may only need `libengine-pkcs11-openssl` here to verify

Once installed, you can check that it can be loaded:

Set the pkcs11 provider and module directly into openssl (make sure `libpkcs11.so` engine reference exists first!)

- `/etc/ssl/openssl.cnf`
```bash
openssl_conf = openssl_def
[openssl_def]
engines = engine_section

[engine_section]
pkcs11 = pkcs11_section

[pkcs11_section]
engine_id = pkcs11
dynamic_path = /usr/lib/x86_64-linux-gnu/engines-1.1/libpkcs11.so
```

```bash
$ ls /usr/lib/x86_64-linux-gnu/engines-1.1/
afalg.so  libpkcs11.so  padlock.so  pkcs11.la  pkcs11.so

$ openssl engine
  (rdrand) Intel RDRAND engine
  (dynamic) Dynamic engine loading support

$ openssl engine -t -c pkcs11
  (pkcs11) pkcs11 engine
  [RSA, rsaEncryption, id-ecPublicKey]
      [ available ]

      dynamic_path = /usr/lib/x86_64-linux-gnu/engines-1.1/libpkcs11.so
```

---

### SOFTHSM

SoftHSM is as the name suggests, a sofware "HSM" module used for testing.   It is ofcourse not hardware backed but the module does allow for a PKCS11 interface which we will also use for testing.

First make sure the softhsm library is installed

- [SoftHSM Install](https://www.opendnssec.org/softhsm/)

Setup a config file where the `directories.tokendir` points to a existing folder where softHSM will save all its data (in this case its `./tokens/`)

```bash
mkdir tokens
```

Edit `softhsm.conf`
and edit the value for `directories.tokendir`

```bash
log.level = DEBUG
objectstore.backend = file
directories.tokendir = /absolute/path/to/pkcs11_signer/misc/tokens/
slots.removable = true
```

Now, make sure that the installation created the softhsm module for openssl:  `[PATH]/libsofthsm2.so`. My softhsm
module is at: `/usr/local/lib/softhsm/libsofthsm2.so`.

```bash
openssl engine dynamic \
 -pre SO_PATH:/usr/lib/x86_64-linux-gnu/engines-1.1/libpkcs11.so \
 -pre ID:pkcs11 -pre LIST_ADD:1 \
 -pre LOAD \
 -pre MODULE_PATH:/usr/local/lib/softhsm/libsofthsm2.so \
 -t -c

  (dynamic) Dynamic engine loading support
  [Success]: SO_PATH:/usr/lib/x86_64-linux-gnu/engines-1.1/libpkcs11.so
  [Success]: ID:pkcs11
  [Success]: LIST_ADD:1
  [Success]: LOAD
  [Success]: MODULE_PATH:/usr/local/lib/softhsm/libsofthsm2.so
  Loaded: (pkcs11) pkcs11 engine
  [RSA, rsaEncryption, id-ecPublicKey]
      [ available ] 
```

Use [pkcs11-too](https://manpages.debian.org/testing/opensc/pkcs11-tool.1.en.html) which comes with the installation of opensc

```bash
export SOFTHSM2_CONF=/absolute/path/to/pkcs11_signer/misc/softhsm.conf

## init softhsm
pkcs11-tool --module /usr/local/lib/softhsm/libsofthsm2.so --slot-index=0 --init-token --label="token1" --so-pin="123456"

## Change pin
pkcs11-tool --module /usr/local/lib/softhsm/libsofthsm2.so  --label="token1" --init-pin --so-pin "123456" --pin mynewpin
```

### Generate mTLS certs

At this point, we can generate mTLS certificate and private key, and import private key into SoftHSM.

```bash
$ /opt/google/endpoint-verification/bin/apihelper --print_certificate
```

This command will print out the following:
```
-----BEGIN CERTIFICATE-----
<omitted>
-----END CERTIFICATE-----
-----BEGIN PRIVATE KEY-----
<omitted>
-----END PRIVATE KEY-----
```

Copy the private key part (everything including `-----BEGIN PRIVATE KEY-----` and `-----END PRIVATE KEY-----`) to a
key.pem file, then generate a key.der file with openSSL.
```bash
$ openssl ec -inform PEM -outform DER -in key.pem -out key.der
```

Now we can import the private key into SoftHSM.
```bash
$ export SOFTHSM2_CONF=/absolute/path/to/pkcs11_signer/misc/softhsm.conf

# Import the private key into SoftHSM
$ pkcs11-tool  --module /usr/local/lib/softhsm/libsofthsm2.so --pin mynewpin \
   --write-object key.der --type privkey --id 1111 --label mtlskey --slot-index 0

# List the objects in SoftHSM, make sure we have the key.
$ pkcs11-tool --module /usr/local/lib/softhsm/libsofthsm2.so  --list-objects --pin mynewpin
    Using slot 0 with a present token (0x828d64)
Private Key Object; EC
  label:      mtlskey
  ID:         1111
  Usage:      decrypt, sign, unwrap
  Access:     sensitive
```
## Run the sample application

First we need to set the credentials. The project is `sijunliu-dca-test`, and we need to copy the
user credential json file to `~/.config/gcloud/application_default_credentials.json`, or set
`GOOGLE_APPLICATION_CREDENTIALS` to the user credential json file path.

Then edit `sample.py`, fill in the cert and key, then run `python sample.py`. The first sample runs
with the cert and key PEM bytes, the second sample uses the cert PEM bytes but the key from SoftHSM.

You should see:
```
python sample.py 
{}

{}
```

Then replace `f'https://pubsub.mtls.googleapis.com/v1/projects/{project}/topics')` with 
`f'https://pubsub.googleapis.com/v1/projects/{project}/topics')`, and run `python sample.py` again. 
You should see both fail with 403 error since we changed mTLS endpoint to regular endpoint.
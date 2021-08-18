rm -rf tokens/*
rm -f *.der
rm -f new-ec*
rm -f rsa*

echo "==== initializing softHSM =========================="
pkcs11-tool --module /usr/local/lib/softhsm/libsofthsm2.so --slot-index=0 --init-token --label="token1" --so-pin="123456"
pkcs11-tool --module /usr/local/lib/softhsm/libsofthsm2.so  --label="token1" --init-pin --so-pin "123456" --pin mynewpin

# For EC keys
echo "==== writing existing EC keys =========================="
openssl ec -inform PEM -outform DER -in key.pem -out key.der
openssl x509 -inform PEM -outform DER -in cert.pem -out cert.der

pkcs11-tool  --module /usr/local/lib/softhsm/libsofthsm2.so --pin mynewpin \
   --write-object key.der --type privkey --id 1111 --label mtlskey --slot-index 0

pkcs11-tool  --module /usr/local/lib/softhsm/libsofthsm2.so --pin mynewpin \
   --write-object cert.der --type cert --id 1111 --label mtlskey --slot-index 0


# For self generated EC keys
echo "==== creating and writing new EC keys =========================="
openssl ecparam -name secp521r1 -genkey -param_enc explicit -out new-ec-key.pem
openssl req -new -x509 -key new-ec-key.pem -out new-ec-cert.pem -days 730

openssl ec -inform PEM -outform DER -in new-ec-key.pem -out new-ec-key.der
openssl x509 -inform PEM -outform DER -in new-ec-cert.pem -out new-ec-cert.der

pkcs11-tool  --module /usr/local/lib/softhsm/libsofthsm2.so --pin mynewpin \
   --write-object new-ec-key.der --type privkey --id 3333 --label neweckey --slot-index 0

pkcs11-tool  --module /usr/local/lib/softhsm/libsofthsm2.so --pin mynewpin \
   --write-object new-ec-cert.der --type cert --id 3333 --label neweckey --slot-index 0

# For self generated RSA keys
echo "==== creating and writing new RSA keys =========================="
openssl req -nodes -x509 -newkey rsa:4096 -keyout rsakey.pem -out rsacert.pem -days 3650

openssl rsa -inform PEM -outform DER -in rsakey.pem -out rsakey.der
openssl x509 -inform PEM -outform DER -in rsacert.pem -out rsacert.der

pkcs11-tool  --module /usr/local/lib/softhsm/libsofthsm2.so --pin mynewpin \
   --write-object rsakey.der --type privkey --id 2222 --label rsakey --slot-index 0
pkcs11-tool  --module /usr/local/lib/softhsm/libsofthsm2.so --pin mynewpin \
   --write-object rsacert.der --type cert --id 2222 --label rsakey --slot-index 0

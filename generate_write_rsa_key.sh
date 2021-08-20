# generate RSA cert/key
openssl req -nodes -x509 -newkey rsa:4096 -keyout rsa-key.pem -out rsa-cert.pem -days 3650

# Write RSA cert/key to HSM, label is "rsakey"
pkcs11-tool  --module /usr/local/lib/softhsm/libsofthsm2.so --pin mynewpin \
   --write-object rsa-key.pem --type privkey --id 2222 --label rsakey --slot-index 0
pkcs11-tool  --module /usr/local/lib/softhsm/libsofthsm2.so --pin mynewpin \
   --write-object rsa-cert.pem --type cert --id 2222 --label rsakey --slot-index 0
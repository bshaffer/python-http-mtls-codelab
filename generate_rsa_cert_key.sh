openssl req -nodes -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 3650

openssl rsa -inform PEM -outform DER -in rsakey.pem -out rsakey.der
openssl x509 -inform PEM -outform DER -in rsacert.pem -out rsacert.der

pkcs11-tool  --module /usr/local/lib/softhsm/libsofthsm2.so --pin mynewpin \
   --write-object rsakey.der --type privkey --id 2222 --label rsakey --slot-index 0


openssl ecparam -name secp521r1 -genkey -param_enc explicit -out new-ec-key.pem
openssl req -new -x509 -key new-ec-key.pem -out new-ec-cert.pem -days 730
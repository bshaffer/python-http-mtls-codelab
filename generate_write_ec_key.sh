# generate ECC cert/key
openssl ecparam -noout -name prime256v1 -genkey -out ec-key.pem -outform PEM
openssl req -new -x509 -key ec-key.pem -out ec-cert.pem -days 730

# Write ECC key to HSM, label is "eckey"
pkcs11-tool  --module /usr/local/lib/softhsm/libsofthsm2.so --pin mynewpin \
   --write-object ec-key.pem --type privkey --id 3333 --label eckey --slot-index 0
pkcs11-tool  --module /usr/local/lib/softhsm/libsofthsm2.so --pin mynewpin \
   --write-object ec-cert.pem --type cert --id 3333 --label eckey --slot-index 0
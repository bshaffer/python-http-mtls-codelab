export SOFTHSM2_CONF=./softhsm.conf

rm -rf tokens/*

pkcs11-tool --module /usr/local/lib/softhsm/libsofthsm2.so --slot-index=0 --init-token --label="token1" --so-pin="123456"
pkcs11-tool --module /usr/local/lib/softhsm/libsofthsm2.so  --label="token1" --init-pin --so-pin "123456" --pin mynewpin

pkcs11-tool  --module /usr/local/lib/softhsm/libsofthsm2.so --pin mynewpin \
   --write-object key.pem --type privkey --id 1111 --label mtlskey --slot-index 0
pkcs11-tool  --module /usr/local/lib/softhsm/libsofthsm2.so --pin mynewpin \
   --write-object cert.pem --type cert --id 1111 --label mtlskey --slot-index 0
#!/usr/bin/env bash
mkdir keys
cd keys

# Generate a self signed certificate for the CA along with a key.
mkdir -p ca/private
chmod 700 ca/private
# NOTE: I'm using -nodes, this means that once anybody gets
# their hands on this particular certificate they can become this CA.
openssl req \
    -x509 \
    -nodes \
    -days 3650 \
    -newkey rsa:4096 \
    -keyout ca/private/ca_key.pem \
    -out ca/ca_cert.pem \
    -subj "/C=US/ST=Acme State/L=Acme City/O=Acme Inc./CN=0.0.0.0"

# Create server private key and certificate request
mkdir -p server/private
chmod 700 ca/private
openssl genrsa -out server/private/server_key.pem 4096
openssl req -new \
    -key server/private/server_key.pem \
    -out server/server.csr \
    -subj "/C=US/ST=Acme State/L=Acme City/O=Acme Inc./CN=0.0.0.0"

# Create client private key and certificate request
mkdir -p client/private
chmod 700 client/private
openssl genrsa -out client/private/client_key.pem 4096
openssl req -new \
    -key client/private/client_key.pem \
    -out client/client.csr \
    -subj "/C=US/ST=Acme State/L=Acme City/O=Acme Inc./CN=0.0.0.0"

# Generate certificates
openssl x509 -req -days 1460 -in server/server.csr \
    -CA ca/ca_cert.pem -CAkey ca/private/ca_key.pem \
    -CAcreateserial -out server/server_cert.pem
openssl x509 -req -days 1460 -in client/client.csr \
    -CA ca/ca_cert.pem -CAkey ca/private/ca_key.pem \
    -CAcreateserial -out client/client_cert.pem

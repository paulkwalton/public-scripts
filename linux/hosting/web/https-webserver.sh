import os
import http.server
import socketserver
import ssl
import tempfile
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timedelta

def generate_self_signed_certificate(cert_path, key_path):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
    ])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=365))
        .sign(key, hashes.SHA256(), default_backend())
    )

    with open(key_path, 'wb') as f:
        f.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    with open(cert_path, 'wb') as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = super().translate_path(path)
        root = os.path.abspath('/opt')
        return os.path.join(root, os.path.relpath(path, os.getcwd()))

PORT = 8000
Handler = CustomHTTPRequestHandler
httpd = socketserver.TCPServer(("", PORT), Handler)

# Generate self-signed certificate and private key files
cert_file = tempfile.NamedTemporaryFile(delete=False)
key_file = tempfile.NamedTemporaryFile(delete=False)
generate_self_signed_certificate(cert_file.name, key_file.name)

ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(certfile=cert_file.name, keyfile=key_file.name)

httpd.socket = ssl_context.wrap_socket(httpd.socket, server_side=True)

print("This script does the following:")
print("1. Generates a self-signed certificate and private key files.")
print("2. Sets the website root to /opt.")
print("3. Starts an HTTPS server on https://localhost:8000.")
print("4. Allows browsing and downloading files from /opt.")
print("5. Removes temporary files after the server stops.")
print("\nServing on https://localhost:8000")
httpd.serve_forever()

# Clean up temporary files after the server stops
cert_file.close()
key_file.close()
os.unlink(cert_file.name)
os.unlink(key_file.name)

import bcrypt
import yaml

# Data user dengan password plaintext
users_plain = {
    "admin": {"password": "admin123", "name": "admin"},
    "petugas": {"password": "petugas123", "name": "petugas"},
    "petugas1": {"password": "petugas321", "name": "petugas2"},
    "petugas2": {"password": "petugas456", "name": "petugas3"},
    "petugas3": {"password": "petugas789", "name": "petugas4"},
    "petugas4": {"password": "petugas111", "name": "petugas5"},
}

# Hash semua password
for user, data in users_plain.items():
    hashed = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt()).decode()
    data["password"] = hashed

# Simpan ke users.yaml
with open("config/users.yaml", "w") as f:
    yaml.dump({"users": users_plain}, f)

print("✅ Password sudah di-hash dan file users.yaml diperbarui.")

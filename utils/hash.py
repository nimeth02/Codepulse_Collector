import hashlib

def hash_id(id):
    checksum = hashlib.sha256(id.encode("utf-8")).hexdigest()
    return checksum
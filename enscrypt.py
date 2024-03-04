import os
import scrypt
import base64
# Hàm tạo hash từ mật khẩu
def create_hash(password, salt):
    N = 2**14  # số lượng lượng bước
    r = 8      # số lần lặp
    p = 1      # paralellization factor

    if salt is None:
        salt = os.urandom(16) 

    # Sử dụng scrypt để tạo hash
    hashed_password = scrypt.hash(password, salt, N=N, r=r, p=p)
    encoded_salt = base64.b64encode(salt).decode('utf-8')
    encoded_hashed_password = base64.b64encode(hashed_password).decode('utf-8')
    return encoded_hashed_password, encoded_salt

# Hàm kiểm tra mật khẩu
def verify_password(stored_hash, input_password, salt):
    decoded_salt = base64.b64decode(salt)
    decoded_stored_hash = base64.b64decode(stored_hash)
    return decoded_stored_hash == scrypt.hash(input_password, decoded_salt)


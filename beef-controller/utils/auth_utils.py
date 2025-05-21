import bcrypt, csv

def hash_password(password: str):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return salt.decode(), hashed.decode()

def load_users(user_file_path: str):
    users = []
    with open(user_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            users.append({
                "username": row["username"],
                "role": row["role"],
                "salt": row["salt"],
                "password_hash": row["password_hash"]
            })
    return users

def authenticate(username: str, password: str, users: list):
    user = None
    for u in users:
        if u["username"] == username:
            user = u
            break
    if not user:
        return {"auth":False, "username": None, "role": None}  # User not found
    # Check the password using bcrypt
    return {
        "auth":bcrypt.checkpw(password.encode('utf-8'), user["password_hash"].encode('utf-8')),
        "username":user["username"],
        "role": user["role"]}

def add_user(username: str, password: str, role: str, user_file_path: str):
    users = load_users(user_file_path)
    for u in users:
        if u["username"] == username:
            return False # user already exists

    salt, hashed = hash_password(password)
    with open(user_file_path, "a", newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([username, role, salt, hashed])
    return True
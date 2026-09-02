from auth import verify_password
import bcrypt

pwd = "040926LITlit!€"
salt = bcrypt.gensalt()
real_hash = bcrypt.hashpw(pwd.encode('utf-8'), salt).decode('utf-8')

with open("main.py", "r") as f:
    content = f.read()

content = content.replace("$2b$12$0N0Jc9J/Zc173yJ8i.q2rOGv24N.17P7I.C.L49G345Q6k.y46Qv6", real_hash)

with open("main.py", "w") as f:
    f.write(content)

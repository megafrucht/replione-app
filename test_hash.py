from auth import verify_password
import os

ADMIN_PASSWORD_HASH = "$2b$12$0N0Jc9J/Zc173yJ8i.q2rOGv24N.17P7I.C.L49G345Q6k.y46Qv6"
pwd = "040926LITlit!€"
print("Result:", verify_password(pwd, ADMIN_PASSWORD_HASH))

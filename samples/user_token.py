
from itsdangerous import URLSafeTimedSerializer
from env import SECRET_KEY, SECURITY_SALT
import time

email = "myemailaddress@gatech.edu"

serializer = URLSafeTimedSerializer(SECRET_KEY)
token = serializer.dumps(email, salt=SECURITY_SALT)

print(token)
# eyJpZCI6NSwibmFtZSI6Iml0c2Rhbmdlcm91cyJ9.6YP6T0BaO67XP--9UzTrmurXSmg

time.sleep(10)

try:
    decoded_email = serializer.loads(
        token,
        salt=SECURITY_SALT,
        max_age=5
    )
    
    print(decoded_email)
    #myemailaddress@gatech.edu

except Exception as e:
    print("expired token")
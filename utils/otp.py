import random
import time

def generate_otp(length=6):
    return ''.join(str(random.randint(0, 9)) for _ in range(length))


def create_otp_with_expiry(length=6, expiry_seconds=300):
    otp = generate_otp(length)
    expiry_time = time.time() + expiry_seconds
    
    return {
        "otp": otp,
        "expires_at": expiry_time
    }


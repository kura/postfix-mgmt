import base64
import hashlib
import bcrypt
import hmac
import pdb
from postfixmgmt.config import *
from postfixmgmt import smart_str


latest_key_id = max(HMAC_KEYS.keys())
shared_key = HMAC_KEYS[latest_key_id]


def md5_password(password):
    m = hashlib.md5()
    m.update(password)
    return m.hexdigest()

def _hmac_create(userpwd, shared_key):
    hmac_value = base64.b64encode(hmac.new(
        smart_str(shared_key), smart_str(userpwd), hashlib.sha512).digest())
    return hmac_value

def _bcrypt_create(hmac_value):
    bcrypt_value = bcrypt.hashpw(hmac_value, bcrypt.gensalt(12))
    return bcrypt_value

def create_password(userpwd):
    return ''.join((
                   'bcrypt', _bcrypt_create(_hmac_create(userpwd, shared_key)),
                   '$', latest_key_id))

def check_user_password(user, raw_password):
    from postfixmgmt.models import db, Admin

    algo_and_hash, key_ver = user.password.rsplit('$', 1)
    try:
        ushared_key = HMAC_KEYS[key_ver]
    except KeyError:
        return False    
    
    if check_password(user.password, raw_password):
        if key_ver != shared_key:
            p = create_password(raw_password)
            user.password = p
            db.session.add(user)
            db.session.commit()
        return True

def check_password(enc_password, raw_password):
    algo_and_hash, key_ver = enc_password.rsplit('$', 1)
    try:
        ushared_key = HMAC_KEYS[key_ver]
    except KeyError:
        return False

    bc_value = algo_and_hash[6:]
    hmac_value = _hmac_create(raw_password, ushared_key)
    return _bcrypt_verify(hmac_value, bc_value)

def _bcrypt_verify(hmac_value, bcrypt_value):
    """Verify an hmac hash against a bcrypt value."""
    return bcrypt.hashpw(hmac_value, bcrypt_value) == bcrypt_value

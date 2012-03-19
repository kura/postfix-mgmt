import os
from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy
from postfixmgmt.config import *


__version__ = "Postfix MGMT 0.0.1 Alpha"


app = Flask(__name__)
app.debug = True
app.secret_key = os.urandom(128)
app.config['SQLALCHEMY_DATABASE_URI'] = DB
db = SQLAlchemy(app)


# Lifted from Django
def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'): 
    """ 
    Returns a bytestring version of 's', encoded as specified in 'encoding'. 

    If strings_only is True, don't convert (some) non-string-like objects. 
    """ 
    if strings_only and isinstance(s, (types.NoneType, int)):
        return s
    if not isinstance(s, basestring): 
        try: 
            return str(s) 
        except UnicodeEncodeError: 
            return unicode(s).encode(encoding, errors) 
    elif isinstance(s, unicode): 
        return s.encode(encoding, errors) 
    elif s and encoding != 'utf-8': 
        return s.decode('utf-8', errors).encode(encoding, errors) 
    else: 
        return s  


import base64
import zlib as bz2

def encrypt(seed):
    return base64.b64encode(bz2.compress(seed))

def decrypt(code):
    return bz2.decompress(base64.b64decode(code))
    

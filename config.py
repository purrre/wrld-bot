import os
from dotenv import load_dotenv

DEV = False
DEV_PREFIX = ',,'

# boost level: upload size
upload_limits = {
    0: 10,
    1: 25,
    2: 50,
    3: 100

}

from datetime import datetime 
import pandas as pd

def get_local_timestamp():
    """
    This function returns the actual time
    """

    return int(str(datetime.now().timestamp())[0:10])





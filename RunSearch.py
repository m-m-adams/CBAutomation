import time
import os
import codecs
import pandas as pd
from cbapi.response import CbEnterpriseResponseAPI, Sensor, SensorGroup, Process


if __name__ == '__main__':
    cb = CbEnterpriseResponseAPI()
    query = cb.select(Process).where("crossproc_count:[100 TO *]").sort("last_update desc")
    results = pd.DataFrame()
    for result in query:
        print(len(result.all_regmods()))


# helper class
from datetime import datetime

def logs(filename, user_operation):
    if filename=="pyclient.py":
        logdataC = open("logdataClient.txt", "a+", encoding="utf-8")
        logdataC.write(
            "\n| TIME >> {} | REQUEST FİLE >> {} | ACTION >> {} |".format(datetime.now(), filename,
                                                                                             user_operation))
        logdataC.close()
    else:
        logdataS = open("logdataServer.txt", "a+", encoding="utf-8")
        logdataS.write(
            "\n| TIME >> {} | REQUEST FİLE >> {} | ACTION >> {} |".format(datetime.now(), filename,
                                                                                             user_operation))
        logdataS.close()


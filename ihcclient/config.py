import logging

## IP adresse og port ihcclient.py skal lytte paa 
HOST, PORT = "192.168.1.4", 10099
## Timeout paa waitForResourceValueChanges kald
EVENTWAIT = 15
## IP adresse paa IHC Controller
IHC_CON = 'https://192.168.1.3'
## IHC User
IHC_USER = 'xxxxx'
## IHC Password
IHC_PASS = 'xxxxxx'
## Log level - Se http://docs.python.org/library/logging.html
LOGLEVEL = logging.INFO

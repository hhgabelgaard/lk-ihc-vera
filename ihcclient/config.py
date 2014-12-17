##############################################################################
#
#    IHC Client
#    Copyright (C) 2014 Hans Henrik Gabelgaard
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging

# IP adresse og port ihcclient.py skal lytte paa
HOST, PORT = "192.168.1.4", 10099
# Timeout paa waitForResourceValueChanges kald
EVENTWAIT = 15
# IP adresse paa IHC Controller
IHC_CON = 'https://192.168.1.3'
# IHC User
IHC_USER = 'xxxxx'
# IHC Password
IHC_PASS = 'xxxxxx'
# Log level - Se http://docs.python.org/library/logging.html
LOGLEVEL = logging.INFO

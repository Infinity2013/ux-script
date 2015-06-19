from infocollector import collector as ic
from mysqlwrapper import wrapper as sw
from qalaunchtime import init_dir
import re
import os
abc = "a bc"
print re.sub(r"\s+", "_", abc)
print abc

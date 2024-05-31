
from memory_profiler import profile

from ais_tools.core import checksum
from ais_tools.core import checksum_str
from ais_tools.core import is_checksum_valid

def run_checksum(n):
    for i in range(n):
        str = ''.join(['a','b'])
        c = checksum(str)
        c = checksum_str(str)
        c = is_checksum_valid(str)


@profile
def run_test():
    run_checksum(1000000)


run_test()
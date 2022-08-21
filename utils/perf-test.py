import timeit
import cProfile
import pstats
from pstats import SortKey
from ais_tools.aivdm import AIVDM, AisToolsDecoder
# from ais_tools.aivdm import LibaisDecoder


# nmea = "!AIVDM,1,1,,A,I00000004000,0*5B"
type_1 = "!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49"
type_18 = '!AIVDM,1,1,,A,B>cSnNP00FVur7UaC7WQ3wS1jCJJ,0*73'

tests = [type_1, type_18]

for nmea in tests:
    print(nmea)
    print(timeit.timeit(f'AIVDM(decoder=AisToolsDecoder()).decode("{nmea}")',
                        setup='from ais_tools.aivdm import AIVDM,LibaisDecoder,AisToolsDecoder',
                        number=10000)
          )
    print()


decoder = AIVDM(AisToolsDecoder())


def do_something():
    for i in range(1000):
        decoder.decode(type_18)


cProfile.run('do_something()', 'perf-test.stats')

p = pstats.Stats('perf-test.stats')
p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(20)

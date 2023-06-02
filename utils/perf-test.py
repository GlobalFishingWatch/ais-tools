import timeit
import cProfile
import pstats
from pstats import SortKey
from ais_tools.aivdm import AIVDM, AisToolsDecoder
from ais_tools.tagblock import update_tagblock
# from ais_tools.aivdm import LibaisDecoder


# nmea = "!AIVDM,1,1,,A,I00000004000,0*5B"
type_1 = "!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49"
type_18 = '!AIVDM,1,1,,A,B>cSnNP00FVur7UaC7WQ3wS1jCJJ,0*73'

message1 = "\\s:66,c:1664582400*32\\!AIVDM,1,1,,A,15D`f63P003R@s6@@`D<Mwwp2`Rq,0*05"
message2 = "\\g:1-2-2243,s:66,c:1664582400*47" \
           "\\!AIVDM,2,1,1,B,5:U7dET2B4iE17KOS:0@Di0PTqE>22222222220l1@F65ut8?=lhCU3l,0*71" \
           "\\g:2-2-2243*5A" \
           "\\!AIVDM,2,2,1,B,p4l888888888880,2*36"

def libais_vs_aistools():
    tests = [type_1, type_18]

    for nmea in tests:
        print(nmea)
        print(timeit.timeit(f'AIVDM(decoder=AisToolsDecoder()).decode("{nmea}")',
                            setup='from ais_tools.aivdm import AIVDM,LibaisDecoder,AisToolsDecoder',
                            number=10000)
              )
        print()


def checksum_compare():
    str = 'A' * 30
    num_iterations = 1000000
    print('checksum_str',
          timeit.timeit(f'checksumstr("{str}")',
                        setup='from ais_tools.checksum import checksumstr',
                        number=num_iterations)
          )
    print('checksumStr',
          timeit.timeit(f'checksumStr("{str}")',
                        setup='from ais.stream.checksum import checksumStr',
                        number=num_iterations)
          )


decoder = AIVDM(AisToolsDecoder())


def decode(n):
    for i in range(n):
        decoder.decode(type_1)


def full_decode(n):
    for i in range(n):
        msg = decoder.safe_decode(message1, best_effort=True)
        msg.add_source('source')
        msg.add_uuid()
        msg.add_parser_version()


def update_tgblock(n):
    for i in range(n):
        update_tagblock(message1, tagblock_text='T')

def run_perf_test(func):
    cProfile.run(func, 'perf-test.stats')

    p = pstats.Stats('perf-test.stats')
    p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(20)


def main():
    run_perf_test('update_tgblock(1000000)')
    # run_perf_test('decode(10000)')
    # run_perf_test('full_decode(100000)')
    # checksum_compare()


if __name__ == "__main__":
    main()

import timeit

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

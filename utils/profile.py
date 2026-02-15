import argparse
import cProfile
import pstats
import time
from pstats import SortKey

from ais_tools.aivdm import AIVDM, AisToolsDecoder
from ais_tools.core import checksum_str
from ais_tools.normalize import normalize_dedup_key


type_1 = "!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49"

message1 = "\\s:66,c:1664582400*32\\!AIVDM,1,1,,A,15D`f63P003R@s6@@`D<Mwwp2`Rq,0*05"
message2 = (
    "\\g:1-2-2243,s:66,c:1664582400*47"
    "\\!AIVDM,2,1,1,B,5:U7dET2B4iE17KOS:0@Di0PTqE>22222222220l1@F65ut8?=lhCU3l,0*71"
    "\\g:2-2-2243*5A"
    "\\!AIVDM,2,2,1,B,p4l888888888880,2*36"
)

decoder = AIVDM(AisToolsDecoder())

# Pre-decode a type 18 message for encode profiling (type 1 is not encodable)
type_18 = "!AIVDM,1,1,,A,B>cSnNP00FVur7UaC7WQ3wS1jCJJ,0*73"
_decoded_type18 = decoder.decode(type_18)


def decode_type1(n):
    for _ in range(n):
        decoder.decode(type_1)


def decode_type5(n):
    for _ in range(n):
        decoder.safe_decode(message2, best_effort=True)


def full_pipeline(n):
    for _ in range(n):
        msg = decoder.safe_decode(message1, best_effort=True)
        msg.add_source('source')
        msg.add_uuid()
        msg.add_parser_version()


def encode(n):
    for _ in range(n):
        decoder.encode(_decoded_type18)


def checksum(n):
    s = "AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0"
    for _ in range(n):
        checksum_str(s)


def dedup_key(n):
    msg = {
        'tagblock_timestamp': 123456789,
        'nmea': "\\!AIVDM,2,1,1,B,5:U7dET2B4iE17KOS:0@Di0PTqE>22222222220l1@F65ut8?=lhCU3l,0*71"
    }
    for _ in range(n):
        normalize_dedup_key(msg)


PROFILES = {
    'decode_type1': (decode_type1, 100_000, "Single-part type 1 decode"),
    'decode_type5': (decode_type5, 100_000, "Multi-part type 5 decode with tagblock"),
    'full_pipeline': (full_pipeline, 100_000, "safe_decode + add_source + add_uuid + add_parser_version"),
    'encode': (encode, 100_000, "Encode a decoded message back to NMEA"),
    'checksum': (checksum, 1_000_000, "C extension checksum_str"),
    'dedup_key': (dedup_key, 1_000_000, "normalize_dedup_key (xxhash-based)"),
}


def run_profile(name, n):
    func, default_n, description = PROFILES[name]
    if n is None:
        n = default_n

    print(f"Profile: {name} — {description}")
    print(f"Iterations: {n:,}")
    print()

    start = time.perf_counter()
    cProfile.runctx(f'{name}({n})', globals(), locals(), 'perf-test.stats')
    elapsed = time.perf_counter() - start

    p = pstats.Stats('perf-test.stats')
    p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(30)

    ops_per_sec = n / elapsed
    print(f"Total: {elapsed:.3f}s | {ops_per_sec:,.0f} ops/sec")


def main():
    parser = argparse.ArgumentParser(description="Profile ais-tools operations")
    parser.add_argument('profile', choices=list(PROFILES.keys()),
                        help="Which profile to run")
    parser.add_argument('-n', type=int, default=None,
                        help="Number of iterations (default depends on profile)")
    args = parser.parse_args()

    run_profile(args.profile, args.n)


if __name__ == "__main__":
    main()

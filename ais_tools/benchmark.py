"""
Benchmark suite for ais-tools operations.
"""

import time

from ais_tools.aivdm import AIVDM
from ais_tools.core import checksum_str
from ais_tools.normalize import normalize_dedup_key


TYPE_1 = "!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49"
TYPE_5 = (
    "\\g:1-2-2243,s:66,c:1664582400*47"
    "\\!AIVDM,2,1,1,B,5:U7dET2B4iE17KOS:0@Di0PTqE>22222222220l1@F65ut8?=lhCU3l,0*71"
    "\\g:2-2-2243*5A"
    "\\!AIVDM,2,2,1,B,p4l888888888880,2*36"
)
TYPE_18 = "!AIVDM,1,1,,A,B>cSnNP00FVur7UaC7WQ3wS1jCJJ,0*73"
TYPE_24 = "!AIVDM,1,1,,B,H>cSnNP@4eEL544000000000000,0*3E"

CHECKSUM_STR = "AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0"
DEDUP_MSG = {
    'tagblock_timestamp': 123456789,
    'nmea': "\\!AIVDM,2,1,1,B,5:U7dET2B4iE17KOS:0@Di0PTqE>22222222220l1@F65ut8?=lhCU3l,0*71"
}

_decoder = AIVDM()
_decoded_18 = _decoder.decode(TYPE_18)
_decoded_24 = _decoder.decode(TYPE_24)


def bench_decode_type_1(n):
    for _ in range(n):
        _decoder.decode(TYPE_1)


def bench_decode_type_5(n):
    for _ in range(n):
        _decoder.safe_decode(TYPE_5)


def bench_decode_type_18(n):
    for _ in range(n):
        _decoder.decode(TYPE_18)


def bench_decode_type_24(n):
    for _ in range(n):
        _decoder.decode(TYPE_24)


def bench_encode_type_18(n):
    for _ in range(n):
        _decoder.encode(_decoded_18)


def bench_encode_type_24(n):
    for _ in range(n):
        _decoder.encode(_decoded_24)


def bench_checksum(n):
    for _ in range(n):
        checksum_str(CHECKSUM_STR)


def bench_dedup_key(n):
    for _ in range(n):
        normalize_dedup_key(DEDUP_MSG)


BENCHMARKS = [
    ("decode type 1", bench_decode_type_1, 100_000),
    ("decode type 5", bench_decode_type_5, 100_000),
    ("decode type 18", bench_decode_type_18, 100_000),
    ("decode type 24", bench_decode_type_24, 100_000),
    ("encode type 18", bench_encode_type_18, 100_000),
    ("encode type 24", bench_encode_type_24, 100_000),
    ("checksum", bench_checksum, 1_000_000),
    ("dedup_key", bench_dedup_key, 1_000_000),
]


def run_benchmarks(iterations=None):
    results = []
    for name, func, default_n in BENCHMARKS:
        n = iterations if iterations is not None else default_n
        start = time.perf_counter()
        func(n)
        elapsed = time.perf_counter() - start
        ops_per_sec = n / elapsed
        results.append((name, n, elapsed, ops_per_sec))
    return results


def format_results(results):
    header = f"{'Benchmark':<22}{'Iterations':>10}{'Time':>10}{'Ops/sec':>12}"
    lines = [header]
    for name, n, elapsed, ops_per_sec in results:
        lines.append(f"{name:<22}{n:>10,}{elapsed:>9.3f}s{ops_per_sec:>12,.0f}")
    return '\n'.join(lines)

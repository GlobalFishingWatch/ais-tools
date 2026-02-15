from click.testing import CliRunner

from ais_tools.benchmark import run_benchmarks, format_results, BENCHMARKS
from ais_tools.cli import benchmark


def test_run_benchmarks():
    results = run_benchmarks(iterations=10)
    assert len(results) == len(BENCHMARKS)
    for name, iterations, elapsed, ops_per_sec in results:
        assert isinstance(name, str)
        assert iterations == 10
        assert elapsed > 0
        assert ops_per_sec > 0


def test_format_results():
    results = run_benchmarks(iterations=10)
    table = format_results(results)
    lines = table.strip().split('\n')
    assert lines[0].startswith('Benchmark')
    assert 'Iterations' in lines[0]
    assert 'Ops/sec' in lines[0]
    assert len(lines) == len(BENCHMARKS) + 1  # header + one row per benchmark


def test_benchmark_cli():
    runner = CliRunner()
    result = runner.invoke(benchmark, args=['-n', '10'])
    assert not result.exception
    lines = result.output.strip().split('\n')
    assert lines[0].startswith('Benchmark')
    assert len(lines) == len(BENCHMARKS) + 1

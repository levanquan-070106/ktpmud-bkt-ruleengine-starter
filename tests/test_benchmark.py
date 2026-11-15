"""Automated Test cho Benchmark do tre p95 (Tieu chi A-07)."""
from scripts.benchmark import run_benchmark


def test_latency_p95_under_100ms():
    """Kiem tra do tre phan loai p95 phai duoi 100ms voi 1.000 ca chay sau warm-up."""
    metrics = run_benchmark(warmup_runs=50, measure_runs=1000)

    assert metrics["runs"] == 1000
    assert metrics["p95_ms"] < 100.0, f"p95 latency {metrics['p95_ms']}ms vuot qua nguong 100ms"
    # Pure Python in-memory thuong dat < 1ms
    assert metrics["p95_ms"] < 5.0, f"p95 latency {metrics['p95_ms']}ms vuot qua nguong ky vong 5ms"

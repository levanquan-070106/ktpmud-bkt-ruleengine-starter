"""Benchmark latency cho Rule Engine WAO/EAACI (Tieu chi A-07).

Yeu cau de bai:
- Benchmark p95 < 100ms voi toi thieu 1.000 luot chay sau warm-up.
- Du lieu kiem thu synthetic, khong dung PII.
"""
from __future__ import annotations

import random
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# Dam bao import duoc rule_engine khi chay truc tiep file script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rule_engine.classifier import classify



def generate_synthetic_payload(idx: int) -> Dict[str, Any]:
    """Sinh payload synthetic da dang theo cac kich ban quy tac khac nhau."""
    scenario = idx % 5
    if scenario == 0:
        # Kich ban R-SOC
        return {
            "tuoi": random.choice([0.5, 5.0, 15.0, 30.0]),
            "huyet_ap_tam_thu": random.choice([60, 75, 85, 88]),
            "co_di_nguyen_nghi_ngo": False,
            "co_ton_thuong_da_niem_mac": True,
            "co_trieu_chung_ho_hap": True,
        }
    elif scenario == 1:
        # Kich ban R01-PV
        return {
            "tuoi": 25.0,
            "huyet_ap_tam_thu": 120,
            "co_di_nguyen_nghi_ngo": False,
            "co_ton_thuong_da_niem_mac": True,
            "co_trieu_chung_ho_hap": True,
        }
    elif scenario == 2:
        # Kich ban R02-PV
        return {
            "tuoi": 30.0,
            "huyet_ap_tam_thu": 115,
            "co_di_nguyen_nghi_ngo": True,
            "co_ton_thuong_da_niem_mac": True,
            "co_trieu_chung_tieu_hoa_nang": True,
        }
    elif scenario == 3:
        # Kich ban R03-PV
        return {
            "tuoi": 35.0,
            "huyet_ap_tam_thu": 110,
            "co_di_nguyen_nghi_ngo": True,
            "di_nguyen_qua_duong_hit": False,
            "co_trieu_chung_ho_hap": True,
        }
    else:
        # Kich ban THEO_DOI hoac thieu du lieu
        return {
            "tuoi": random.choice([20.0, None]),
            "huyet_ap_tam_thu": random.choice([120, None]),
            "co_di_nguyen_nghi_ngo": True,
            "co_ton_thuong_da_niem_mac": True,
        }


def run_benchmark(
    warmup_runs: int = 100,
    measure_runs: int = 1000,
) -> Dict[str, float]:
    """Chay benchmark do do tre voi warm-up va tap du lieu do luong."""
    print(f"=== BAT DAU WARM-UP ({warmup_runs} luot chay) ===")
    for i in range(warmup_runs):
        payload = generate_synthetic_payload(i)
        classify(payload)

    print(f"=== BAT DAU DO LUONG ({measure_runs} luot chay) ===")
    latencies_ns: List[int] = []

    for i in range(measure_runs):
        payload = generate_synthetic_payload(i)
        t_start = time.perf_counter_ns()
        classify(payload)
        t_end = time.perf_counter_ns()
        latencies_ns.append(t_end - t_start)

    # Chuyen doi sang milliseconds (ms)
    latencies_ms = [ns / 1_000_000.0 for ns in latencies_ns]
    latencies_ms.sort()

    p50 = statistics.median(latencies_ms)
    p90 = latencies_ms[int(0.90 * len(latencies_ms))]
    p95 = latencies_ms[int(0.95 * len(latencies_ms))]
    p99 = latencies_ms[int(0.99 * len(latencies_ms))]
    mean_val = statistics.mean(latencies_ms)
    min_val = min(latencies_ms)
    max_val = max(latencies_ms)

    metrics = {
        "runs": measure_runs,
        "min_ms": min_val,
        "mean_ms": mean_val,
        "p50_ms": p50,
        "p90_ms": p90,
        "p95_ms": p95,
        "p99_ms": p99,
        "max_ms": max_val,
    }

    print("\n=== KET QUA BENCHMARK DO TRE ===")
    print(f"So luot chay: {measure_runs}")
    print(f"Min:    {min_val:.5f} ms")
    print(f"Mean:   {mean_val:.5f} ms")
    print(f"p50:    {p50:.5f} ms")
    print(f"p90:    {p90:.5f} ms")
    print(f"p95:    {p95:.5f} ms (Yeu cau < 100 ms)")
    print(f"p99:    {p99:.5f} ms")
    print(f"Max:    {max_val:.5f} ms")

    if p95 < 100.0:
        print("\n>> DAT TIEU CHUAN A-07: p95 < 100 ms <<\n")
    else:
        print("\n>> KHONG DAT TIEU CHUAN A-07 <<\n")

    return metrics


if __name__ == "__main__":
    run_benchmark()

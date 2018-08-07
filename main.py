#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from dataloader import *


if __name__ == "__main__":
    benchmarks = BenchmarkData("Winner analysis - data.xlsx")
    benchmarks.printAllMetrics()

    sample = SampleData("Winner analysis - data.xlsx")
    sample.classify(benchmarks.clv_mean, benchmarks.clv_std,
                    benchmarks.qchg_mean, benchmarks.qchg_std,
                    benchmarks.ychg_mean, benchmarks.ychg_std)

    sample.printClassifyResults()

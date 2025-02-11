# main script

import os
import subprocess
import argparse

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Select Benchmark
benchmarks = ["BFS", "SORT", "LRS", "KNN"]
parser = argparse.ArgumentParser(usage='[-b <benchmark>]')
parser.add_argument('-b', '--benchmark', type=str, 
                    default="BFS", choices=benchmarks)
parser.add_argument('-s', '--size', default="1")
args = parser.parse_args()

# Gem5 Command # adapted from piazza post @19 https://piazza.com/class/m4vp7hf1id4dm/post/19
outdir = f"{ROOT_DIR}/{args.benchmark}/m5out-{args.benchmark}-{args.size}"
# workload_path = f"/u/csc368h/winter/pub/workloads/microbench/{workload}/bench"
gem5_script = f"{ROOT_DIR}/{args.benchmark}/{args.benchmark}.py"
gem5_binary = "/u/csc368h/winter/pub/bin/gem5.opt"
gem5_cmd = [
    gem5_binary, 
    f"--outdir={outdir}", 
    gem5_script,
    f"-s {args.size}"]

# Run Benchmark Script
subprocess.run(gem5_cmd)
print("================================")
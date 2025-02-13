# Searching for key metrics and plot

import os
import glob
import argparse
import matplotlib.pyplot as plt

def parse_stats_file(stats_path):
    """
    Return: list of region dictionary.
        maps stat_name -> stat_value.
    """
    regions = []
    current_region_stats = {}
    inside_region = False

    with open(stats_path, 'r') as f:
        for line in f:
            line_stripped = line.strip()
            if "Begin Simulation Statistics" in line_stripped:
                inside_region = True
                current_region_stats = {}
            elif "End Simulation Statistics" in line_stripped:
                inside_region = False
                if current_region_stats:
                    regions.append(current_region_stats)
            elif inside_region:
                if line_stripped and not line_stripped.startswith('#'):
                    parts = line_stripped.split()
                    if len(parts) >= 2:
                        name = parts[0]
                        val_str = parts[1]
                        try:
                            val_float = float(val_str)
                            current_region_stats[name] = val_float
                        except ValueError:
                            current_region_stats[name] = val_str  # non-numeric
    return regions

def extract_metric(regions, region_index, metric_name):
    """
    Return: metric value for region_index
        0=before, 
        1=in, 
        2=after.
    """
    if region_index < len(regions):
        return regions[region_index].get(metric_name, None)
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metric", default="system.cpu.commitStats0.numInsts")
    parser.add_argument("--region", default="before", choices=["before","in","after"])
    parser.add_argument("--pattern", default="*/m5out-*-[0-9]*/stats.txt")
    parser.add_argument("--out_pdf", default="multi_bench_plot.pdf")
    args = parser.parse_args()

    region_idx_map = {"before":0, "in":1, "after":2}
    region_index = region_idx_map[args.region]

    bench_data = {}

    paths = glob.glob(args.pattern)
    if not paths:
        print(f"No files found with pattern: {args.pattern}")
        return

    for stats_file in paths:
        abs_dir = os.path.dirname(stats_file)       # e.g. BFS/m5out-BFS-1
        top_dir = os.path.dirname(abs_dir)          # e.g. BFS
        top_dir_name = os.path.basename(os.path.dirname(stats_file))   # "m5out-BFS-1"
        parent_name  = os.path.basename(os.path.dirname(os.path.dirname(stats_file))) # "BFS"

        # Let's interpret "parent_name" as the benchmark. e.g. BFS, SSSP, PageRank
        benchmark_name = parent_name

        # parse the input size from the sub_dir name e.g.. "m5out-BFS-1"
        parts = top_dir_name.split('-')  # e.g. ["m5out", "BFS", "1"]
        if len(parts) >= 3:
            # The last part is presumably the integer size
            try:
                size_val = int(parts[-1])
            except ValueError:
                size_val = 0
        else:
            size_val = 0

        regions = parse_stats_file(stats_file)

        # extract metric
        val = extract_metric(regions, region_index, args.metric)
        if val is None:
            val = 0.0

        if benchmark_name not in bench_data:
            bench_data[benchmark_name] = []
        bench_data[benchmark_name].append((size_val, val))

    # {bench_name: [(size, val), ...]}
    # sort by 'size' to plot from small to large
    for bench_name in bench_data:
        bench_data[bench_name].sort(key=lambda x: x[0])  # sort by size

    # plot
    os.makedirs("results", exist_ok=True)
    plt.figure(figsize=(8,5))

    for bench_name, data_list in bench_data.items():
        # [(size, val)]
        x_vals = [d[0] for d in data_list]
        y_vals = [d[1] for d in data_list]
        plt.plot(x_vals, y_vals, marker='o', label=bench_name)

    plt.xlabel("Input Size")
    plt.xscale("log")
    plt.ylabel(args.metric)
    # plt.ylim(0, 1e8)
    plt.title(f"{args.metric} in region '{args.region}' (Line per Benchmark)")
    plt.legend()
    plt.tight_layout()

    pdf_path = os.path.join("results", f'{args.metric}_{args.region}_{args.out_pdf}')
    plt.savefig(pdf_path)
    print(f"Plot saved to {pdf_path} (no GUI displayed).")

if __name__ == "__main__":
    main()

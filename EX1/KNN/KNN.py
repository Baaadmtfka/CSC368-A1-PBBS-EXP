# KNN:
#   nearestNeighbors/octTree/neighbors
# Input Data:
#   geometryData/randPoints
# System:
#   CPU: X86TimingSimpleCPU 200MHz
#   MEM: DDR3_1600_8x8 8GB

import os
import m5
from m5.objects import *
import argparse
import subprocess

# Arguments for size of input
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--size', default="1")
args = parser.parse_args()
SIZE = int(args.size)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
### Customize:
DEFAULT_BINARY = '/u/csc368h/winter/pub/workloads/pbbsbench/benchmarks/nearestNeighbors/octTree/neighbors'
DEFAULT_INFILE = f"{ROOT_DIR}/knn-{SIZE}-input"
DEFAULT_OUTFILE = f"{ROOT_DIR}/knn-{SIZE}-output"

INPUT_CMD = [
    "/u/csc368h/winter/pub/workloads/pbbsbench/testData/geometryData/randPoints", 
    "-d", "3", # dimensions
    f"{SIZE*10}", # size
    DEFAULT_INFILE
]
PROCESS_CMD = [
    DEFAULT_BINARY, 
    # "-o", f"{DEFAULT_OUTFILE}",
    "-k", "5", # num of neighbors
    "-d", "3", # dimensions
    DEFAULT_INFILE
]
# Generate Input File
if not os.path.exists(DEFAULT_INFILE):
    print("No existing file, generating input\n================================")
    subprocess.run(INPUT_CMD, 
                cwd=ROOT_DIR, 
                check=True)


# System creation
system = System()
## gem5 needs to know the clock and voltage
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '200MHz'
system.clk_domain.voltage_domain = VoltageDomain() # defaults to 1V
## Create a crossbar so that we can connect main memory and the CPU (below)
system.membus = SystemXBar()
system.system_port = system.membus.cpu_side_ports
## Use timing mode for memory modelling
system.mem_mode = 'timing'
# CPU Setup
system.cpu = X86TimingSimpleCPU()
system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports
## This is needed when we use x86 CPUs
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports
# Memory setup
system.mem_ctrl = MemCtrl()
system.mem_ctrl.port = system.membus.mem_side_ports
## A memory controller interfaces with main memory; create it here
system.mem_ctrl.dram = DDR3_1600_8x8()
## A DDR3_1600_8x8 has 8GB of memory, so setup an 8 GB address range
address_ranges = [AddrRange('8GB')]
system.mem_ranges = address_ranges
system.mem_ctrl.dram.range = address_ranges[0]

# Process setup
process = Process()
binary = DEFAULT_BINARY
process.cmd = PROCESS_CMD

## The necessary gem5 calls to initialize the workload and its threads
system.workload = SEWorkload.init_compatible(binary)
system.cpu.workload = process
system.cpu.createThreads()
# Start the simulation
root = Root(full_system=False, system=system) # must assign a root
m5.instantiate() # must be called before m5.simulate
m5.simulate()

print(f'Finished KNN Benchmark, with input size: {SIZE*10}')

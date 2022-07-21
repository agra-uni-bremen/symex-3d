#!/usr/bin/env python3

import sys
import argparse

from ptrace.process_trace import process_trace_file, parse_block_xml
from ptrace.parse_elf import process_DWARF
    

"""path_dir = "C:/Users/JZ/Documents/Uni/AGRA/symex-visualization/traces/"
path_dir_elf = "C:/Users/JZ/Documents/Uni/AGRA/symex-visualization/binaries/"
path_dir_blocks = "C:/Users/JZ/Documents/Uni/AGRA/symex-visualization/traces/"
path_dir_c = "C:/Users/JZ/Documents/Uni/AGRA/symex-visualization/symex-vp/sw/symex/"
#path_dir += "trace_m-full-symbolic.xml"
#path_dir += "trace_example.xml"
#path_dir += "trace_three_branches.xml"
#path_dir += "trace_fibonacci_c.xml"
#path_dir += "trace_fibonacci_asm.xml"

path_dir += "trace_fibonacci_c.xml" #simple_

path_dir_elf += "MUL.elf"

path_dir_blocks += "fib_c_blocks.xml"

path_dir_c += "fib_c/main.c"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Processes the raw SymEx trace file and outputs a PTrace file. '+ 
                                                'If the path to the binary and source file are specified also creates a .blk file')

    # Required positional argument
    parser.add_argument('--trace', type=str, required=True,
                        help='Path to raw SymEx trace file')

    parser.add_argument('--output', type=str, required=True,
                        help='Output directory')
    parser.add_argument('--elf', type=str, required=False, 
                    help='Path to ELF binary')
    parser.add_argument('--source', type=str, required=False, 
                    help='Path to source file')

    args = parser.parse_args()

    num_runs = process_trace_file(args.trace, args.output)
    if(args.elf and args.source):
        print("ELF and Source path specified. Creating optional .blk file.")
        process_DWARF(args.elf, args.source, args.trace, args.output, num_runs)
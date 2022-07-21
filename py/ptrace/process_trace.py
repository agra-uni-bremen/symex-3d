#import bpy

import random
import math
import os.path
import xml.etree.ElementTree as ET

from enum import Enum
from ptrace.Enums.riscv_enum import Opcode, Opcode_type, Reg, Symbolic_Beh
from ptrace.Data.instructions import Run, Instruction, Arith_Instruction, Jump, Branch, LoadStore, CSR, Analysis_Data, Link_Node, Link_Data
from ptrace.Data.blocks import CFBlock
from ptrace.utils.utils import open_file, save_file_binary, save_file_text, read_xml, confirm, terminal_colors

from ptrace.Data.xml_parser import parse_ptrace_xml, parse_analysis_xml

#from elftools.elf.elffile import ELFFile #TODO fix imports

MAX_STEPS_TO_GENERATE = 10000 #don't create all steps for very large traces

## -- CF analysis and processing -- ##

def parse_block_xml(block_xml_string, path_code):
    b_root = ET.fromstring(block_xml_string)
    cf_blocks_root = b_root[0]#TODO maybe add a check here for correct tag
    functions_root = b_root[1]

    #analyse_trace(root) #todo add modes and merge with create scene

    run_id = 0
    for run in cf_blocks_root:
        for block in run:
            block_start = int(block.attrib.get('block_start'))
            block_end = int(block.attrib.get('block_end'))
            file_name = block.attrib.get('file_name')
            line_start = int(block.attrib.get('line_start'))
            line_end = int(block.attrib.get('line_end'))
            function_name = block.attrib.get('function_name')
            code = ""

            current_block = CFBlock(block_start, block_end, file_name, line_start, line_end, function_name, code)
            #create_block(current_block, run_id+1)
            #location_t = ((block_start - global_start)*INSTRUCTION_DISTANCE+INSTRUCTION_DISTANCE, run_id*RUN_DISTANCE-CUBE_SIZE, BLOCK_Z+CUBE_SIZE)
            name_t = f"cf_code_{hex(block_start)}_{hex(block_end)}_{run_id}"
            text = f"{function_name}" #TODO include code
            #text_obj = create_text(location_t, name_t, text, 2, "mat_text")#TODO calculate location in one place or create block text once for one run

        run_id +=1

    #create function blocks
    for function in functions_root:
        function_name = function.attrib.get('name')
        function_start = int(function.attrib.get('start'))
        function_end = int(function.attrib.get('end'))

        #create_function(function_name, function_start, function_end)
    #read labels and create annotations

def check_ptrace(ptrace):
    steps_missing = []
    print(f"{terminal_colors.HEADER}Checking PTrace{terminal_colors.ENDC}")
    for run in ptrace:
        if(len(run.instruction_list)==0):
            print(f"{terminal_colors.WARNING}[WARNING] Empty instruction list for run [{run.run_id}]\nThis run might be fully identical to its parent and was therefore removed{terminal_colors.ENDC}")
            continue
        if(len(run.instruction_list[0].steps_active)==0):
            print("-------------------------------------------------------------------")
            print(f"{terminal_colors.FAIL}[ERROR] First instruction has no active steps for run [{run.run_id}]{terminal_colors.ENDC}")
            print("-------------------------------------------------------------------")
            return []
        min_step = run.instruction_list[0].steps_active[0][0]
        max_step = -1
        for instruction in run.instruction_list:
            for step_t in instruction.steps_active:
                if(max_step<step_t[0]):
                    max_step=step_t[0]
        print(f"Run {run.run_id}: min_step={min_step} max_step={max_step}")
        for i in range(min_step,max_step+1):
            found_step = False
            for instruction in run.instruction_list:
                if(found_step):
                    break
                for step_t in instruction.steps_active:
                    if(found_step):
                        break
                    if(step_t[0]==i):
                        found_step = True
                        break
            if(not found_step):
                steps_missing.append((run.run_id,i))
        print(f"Run {run.run_id} {terminal_colors.OKGREEN}[OK]{terminal_colors.ENDC}")
    print("PTrace check complete")
    if(len(steps_missing)>0):
        print(f"{terminal_colors.FAIL}Steps missing: {steps_missing}{terminal_colors.ENDC}")
    else:
        print(f"{terminal_colors.OKGREEN}No steps missing{terminal_colors.ENDC}")
    return steps_missing


def analyse_trace(root):
    """
    Perform basic analysis on the trace to be able to detect any large gaps in memory/code later and improve visualization
    """
    global_start = 0
    max_pc = 0
    min_pc = 0xFFFFFF

    num_runs = 0
    run_start = []
    potential_child_branches = []

    timeline_forks = [0] #TODO remove
    
    memory_list = []
    memory_list_per_run = []

    global_start = int(root[0][0][0].attrib.get('pc'),16) #TODO handle different node types
    temp_memory_access_set = set()
    total_accesses = 0
    ##next_timeline_start = -1
    ##next_timeline_parent_id = -1
    ##next_timeline_step = -1
    for entry in root:
        if(entry.tag=="symex"):
            num_runs += 1

            memory_access_current_run = set()
            for stp in entry[0]:
                step_attr = stp.attrib
                pc_hex = step_attr.get('pc')
                pc = int(pc_hex,16)

                if(pc>max_pc):
                    max_pc = pc
                if(pc<min_pc):
                    min_pc = pc

                #check which memoryregions are accessed to create a compressed view later
                if(stp[0].tag == "load" or stp[0].tag == "store"):
                    memory_target = int(stp[0].attrib.get('target'),16)
                    temp_memory_access_set.add(memory_target)
                    memory_access_current_run.add(memory_target)
                    total_accesses += 1
            memory_list_per_run.append(list(memory_access_current_run))
            # index 1 = show registers
            #register_dump = entry[1].text
            #print(register_dump)
            # index 2 = next timeline TODO
            ## if(len(entry)>2 and entry[2].tag=="timeline"):
            ##     next_timeline_start = int(entry[2].attrib.get('branch_pc'),16)
            ##     next_timeline_parent_id = int(entry[2].attrib.get('parent_run'))
            ##     next_timeline_step = int(entry[2].attrib.get('step'))
            ##     print(f"{terminal_colors.BOLD}Start of run {num_runs} with parent {next_timeline_parent_id} that was explored next: step {next_timeline_step} at {next_timeline_start}{terminal_colors.ENDC}")
            ##     #print(next_timeline)
            ## else:
            ##     next_timeline_start = -1
            ##     next_timeline_parent_id = -1
            ##     next_timeline_step = -1
            ##     print("ERROR unexpected entry")
        if(entry.tag=="timelines"):
            tree = Link_Node(None, -1, None) #root
            for id, run_i in enumerate(entry):
                link_data = []
                current_node = tree #for each path/run start at the root
                for branch in run_i:
                    branch_pc = int(branch.attrib.get('pc'),16)
                    branch_step = int(branch.attrib.get('step'))
                    branch_hash = int(branch.attrib.get('hash'))
                    p_data = Link_Data(branch_hash, branch_pc, branch_step)
                    link_data.append(p_data)
                    current_node = current_node.insert(p_data, id, 1)
                potential_child_branches.append(link_data)
            #print(f"tree: {tree.PrintTree()}")
            print(tree.to_xml())
            tree.display()
            run_start.append((-1,0,0))
            for r in range(1,num_runs):
                node = tree.discover_run_start(r)
                if(node):
                    run_start.append((node.run_id,node.data.pc,node.data.step))
                else:
                    print(f"{terminal_colors.FAIL}[ERROR] missing branch data for run {terminal_colors.OKCYAN}{r}{terminal_colors.ENDC}")
            print(run_start)
    memory_list = list(temp_memory_access_set)
    memory_list.sort()
    print(f"{terminal_colors.OKCYAN}Accessed Memory[{total_accesses} -> {len(temp_memory_access_set)}]: {len(memory_list)}{terminal_colors.ENDC}")

    #create parent child run list
    discovered_run_links = []
    for run_id_n in range(num_runs):
        discovered_run_links.append([])

    for run_id in range(num_runs):
        #if(run_id==0): # all but the first run must have parent runs
            #reached_start= True
            #continue

        for child_id, link in enumerate(run_start):

            if(run_id == link[0]):
                print(f"Child run with id {child_id} found for parent {run_id}")
                discovered_run_links[run_id].append((child_id,run_start[child_id][1], run_start[child_id][2]))
                break



    analysis_results = Analysis_Data(global_start, min_pc, max_pc, num_runs, timeline_forks, run_start, 
                                        potential_child_branches, memory_list, memory_list_per_run)
    analysis_results.discovered_run_links=discovered_run_links
    return analysis_results

def determine_symbolic_behavior(instr_data, reg_rs1, reg_rs2, reg_rd, 
                                    reg_rs1_symbolic, reg_rs2_symbolic, reg_rd_symbolic, rd_was_symbolic):
    if("beh" in instr_data.attrib.keys()):
        beh = instr_data.attrib.get("beh")
        if beh == "none":
            return Symbolic_Beh.none
        elif beh == "destroy":
            return Symbolic_Beh.destroy
        elif beh == "update":
            return Symbolic_Beh.update
        elif beh == "create":
            return Symbolic_Beh.create
        elif beh == "overwrite":
            return Symbolic_Beh.overwrite
        elif beh == "special":
            return Symbolic_Beh.special
        elif beh == "error":
            return Symbolic_Beh.unknown
        else:
            print(f"[ERROR] unknown symbolic behavior for instruction {instr_data}")
            return Symbolic_Beh.unknown
    else:#trace doesn't contain any information about symbolic behavior. Try to infer behavior from available data. 
        if(rd_was_symbolic and not reg_rd_symbolic):
            return Symbolic_Beh.destroy

        #TODO add previous rd
        elif(not reg_rs1_symbolic and not reg_rs2_symbolic and not reg_rd_symbolic):
            return Symbolic_Beh.none

        elif(reg_rd_symbolic and not rd_was_symbolic):
            return Symbolic_Beh.create

        elif(reg_rd_symbolic and rd_was_symbolic):
            if(reg_rd == reg_rs1 or reg_rd == reg_rs2):
                return Symbolic_Beh.update
            else:
                return Symbolic_Beh.overwrite

        else:
            print("ERROR: unknown symbolic behavior")
            return Symbolic_Beh.unknown

def get_instr_reg(instr_data, attrib):
    register = Reg.none
    is_symbolic = False
    if(attrib in instr_data.attrib.keys()):
        register = Reg[instr_data.attrib.get(attrib).split()[0].split("/")[0]] #TODO fix trace registernames so only one split is necessary
        is_symbolic = instr_data.attrib.get(attrib)[-1]=="S"
    return (register,is_symbolic)

def get_imm(instr_data, attrib):
    value = None
    #is_symbolic = False
    if(attrib in instr_data.attrib.keys()):
        value = int(instr_data.attrib.get(attrib).split()[0].split("/")[0])
        #imm_symbolic = instr_data.attrib.get(attrib)[-1]=="S" #unused
    return value

def update_callstack(call_stack, link_reg, link_address):
    """update callstack (depth) if opcode is a jump"""
    depth = len(call_stack)

    if(link_reg!="zero (x0)"):
        call_stack.append(link_address)    
    else:
        if(depth>0):
            expected_return_address = call_stack[depth-1]
            if(link_address == expected_return_address):
                call_stack.pop()

def process_instruction(run, instr, pc, call_stack, reg_rs1, reg_rs2, reg_rd, imm):
    instr_data = instr[0]

    opcode_string = ""
    if(instr_data.tag=="jump"):#TODO maybe refactor this and add opcodename to jump trace data
        opcode_string="JAL"
    elif(instr_data.tag=="ECALL"):
        opcode_string="ECALL"
    else:
        opcode_string = instr_data.get('opcode')
    current_opcode = Opcode[opcode_string]




    #create instruction    
    depth = len(call_stack)
    current_instruction = None
    if(instr_data.tag == "instruction"):
        current_instruction = Arith_Instruction(pc, run, current_opcode, depth=depth, 
                                reg_rs1=reg_rs1, reg_rs2=reg_rs2, reg_rd=reg_rd, imm1=imm)
    elif(instr_data.tag == "ECALL"):
        current_instruction = Instruction(pc, run, current_opcode, depth=depth, type=Opcode_type.ECALL)
    elif(instr_data.tag == "jump"):
        jump_target = int(instr_data.attrib.get("target"),16)
        link_reg = instr_data.attrib.get("link")
        link_address = int(instr_data.attrib.get("link-address"),16)

        current_instruction = Jump(pc, run, current_opcode, depth=depth, target=jump_target, 
                                    link_reg=Reg[link_reg.split()[0].split("/")[0]], link_address=link_address)

        update_callstack(call_stack, link_reg, link_address)

    elif(instr_data.tag == "branch"):
        jump_target =  int(instr_data.attrib.get("target"),16) #int(entry[0][step+1].get('pc'),16)
        branch_edge =  int(instr_data.attrib.get("cond"))
        current_instruction = Branch(pc, run, current_opcode, depth=depth, target=jump_target, 
                                    reg_rs1=reg_rs1, reg_rs2=Reg.none, condition=branch_edge>0)

    elif(instr_data.tag == "load" or instr_data.tag == "store"):
        current_instruction = LoadStore(pc, run, current_opcode, target=int(instr_data.attrib.get("target")[2:],16), #TODO remove 0x from raw trace
                                    reg_rs1=reg_rs1, imm1=None, reg_rs2d=Reg.none, depth=depth)
    elif(instr_data.tag == "csr"):
        current_instruction = CSR(pc, run, current_opcode, -1, depth=depth)
    else:
        current_instruction = Instruction(pc, run, Opcode.ERROR, depth)
        print("ERROR: Unknown opcode")
    return current_instruction

def process_trace(root, analysis_data):

    run_start = analysis_data.run_start
    potential_child_branches = analysis_data.potential_child_branches
    memory_list = analysis_data.memory_list
    print(f"{terminal_colors.HEADER}Processing trace: (with input analysis data [{len(analysis_data.memory_list)}]){terminal_colors.ENDC}")

    run_list = []
    
    run = 0

    for entry in root:
        print(f"Found entry [{entry.tag}]")
        if(entry.tag=="symex"):
            run_entry = entry[0]
            run +=1
            print(f"-> {terminal_colors.BOLD}[Processing run:{run-1}]{terminal_colors.ENDC}")
            #depth = 0
            call_stack = []

            start = int(run_entry[0].attrib.get('pc'),16)
            start_step = int(run_entry[0].attrib.get('step'))

            parent_id = -1
            branch_pc = start
            branch_step = start_step
            if(run_start):
                if(len(run_start)>=run):
                    parent_id = run_start[run-1][0]
                    branch_pc = run_start[run-1][1]
                    branch_step = run_start[run-1][2]
                else:
                     print(f"{terminal_colors.FAIL}[ERROR] missing parent analysis data for run {terminal_colors.OKCYAN}{run-1}{terminal_colors.ENDC}")
            else:
                print(f"{terminal_colors.FAIL}[ERROR] missing run start analysis data for run{terminal_colors.ENDC}")
                

            current_run = Run(run, start)
            current_run.parent_id = parent_id
            pc_end = int(run_entry[-1].attrib.get('pc'),16)
            current_run.end = pc_end
            
            step_counter = -1
            reached_start = False

            #print(f"Number of memory accesses: {len(memory_list)}")


            for instr in run_entry:
                step_counter +=1
                if(step_counter>MAX_STEPS_TO_GENERATE):
                    print(f"{terminal_colors.WARNING}[WARNING]:max steps reached RUN_ID {run}{terminal_colors.ENDC}")
                    break

                instr_data = instr[0]
                step_attr = instr.attrib
                pc_hex = step_attr.get('pc')
                pc = int(pc_hex,16)

                #TODO maybe move this into the analysis section
                if(not reached_start):#dont create any objects if runs is identical to parent
                    #if(pc==branch_start or branch_start==-1 or (pc in potential_child_branches[parent_id])):
                    current_step = int(step_attr.get('step'))
                    #print(f"checking for run {run-1} and parent {parent_id} with pc({pc})==branch_pc{branch_pc} and step [{current_step}/{branch_step}]")
                    #TODO probably need to log previous pc instead of branch pc after jumping
                    if(current_step >= branch_step):
                        if(pc==branch_pc or branch_pc<=0):
                            reached_start = True
                            print(f"-- Reached start of run {terminal_colors.OKBLUE}(removed duplicate trace data up to step {current_step}){terminal_colors.ENDC}")
                            #set parent for current run
                            current_run.start_step=start_step
                            current_run.start_pc=start
                        else:
                            reached_start = True
                            print(f"-- {terminal_colors.OKBLUE}[INFO] Exceeded start step of run (starting from start step {current_step}){terminal_colors.ENDC}")
                            print(f"pc: {hex(pc)}, branch_pc:{hex(branch_pc)}")
                            current_run.start_step=start_step
                            current_run.start_pc=start
                    else:
                        #print(f"skipped pc {hex(pc)} (not {hex(branch_start)})")
                        if(instr_data.tag == "jump"):
                            link_reg = instr_data.attrib.get("link")
                            link_address = int(instr_data.attrib.get("link-address"),16)
                            update_callstack(call_stack, link_reg, link_address)
                        continue # CONTINUE with next loop

                #check if a block was already created for this pc, run and depth
                current_instruction = None
                object_already_exists = False
                for instruction in current_run.instruction_list:
                    if(instruction.depth==len(call_stack) and instruction.pc==pc):
                        object_already_exists = True
                        current_instruction = instruction
                        #print(f"instruction {instruction} already exists")
                        break
        
                #check if any input register or the result is symbolic
                reg_rs1, reg_rs1_symbolic = get_instr_reg(instr_data, "rs1")
                reg_rs2, reg_rs2_symbolic = get_instr_reg(instr_data, "rs2")
                imm = get_imm(instr_data, "imm")
                reg_rd, reg_rd_symbolic = get_instr_reg(instr_data, "rd")
                rd_was_symbolic = False

                symbolic_beh = determine_symbolic_behavior(instr_data, reg_rs1, reg_rs2, reg_rd, 
                                                            reg_rs1_symbolic, reg_rs2_symbolic, reg_rd_symbolic, rd_was_symbolic)

                if(not object_already_exists):
                    current_instruction = process_instruction(run, instr, pc, call_stack, reg_rs1, reg_rs2, reg_rd, imm)
                if(current_instruction==None):
                    print("ERROR: instruction block wasn't created") #should be unreachable if all are implemented
                
                step_attr = instr.attrib
                step_str = step_attr.get('step')
                step = int(step_str)

                if((step, symbolic_beh) in current_instruction.steps_active):
                    print("ERROR: encountered duplicate step")
                    print(f"step={step} pc={hex(pc)} op={current_instruction.opcode.name}")
                if(instr_data.tag == "branch"): #branches have a condition that can change between loops
                    branch_edge =  int(instr_data.attrib.get("cond"))
                    current_instruction.add_active_step(step, symbolic_beh, branch_edge)
                else:
                    current_instruction.add_active_step(step, symbolic_beh)
                if(not object_already_exists):
                    current_run.instruction_list.append(current_instruction)
            if(not reached_start):
                print(f"{terminal_colors.FAIL}[ERROR] could not find start for child run [{run-1}] and parent [{parent_id}]{terminal_colors.ENDC}")
            print("      -- Done --\n")
            #Done processing this run
            current_run.num_steps = step_counter
            run_list.append(current_run)
        #else: not a symex run entry
    return run_list

def process_trace_file(input_path, output_path):
    while(input_path==""):
        print(f"{terminal_colors.FAIL}[ERROR] empty input path{terminal_colors.ENDC}")
        input_path = input("Specify new path to trace:")
    
    tree,root = read_xml(input_path)

    path, file = os.path.split(input_path) #input_path.split("/")[-1].split(".")[0]
    executable_name = file.split(".")[0]
    print(f"{terminal_colors.HEADER}[Start processing trace {executable_name}]{terminal_colors.ENDC}")

    analysis_results = analyse_trace(root)
    print(f"{terminal_colors.OKGREEN}[Trace analysis complete]{terminal_colors.ENDC}")
    ptrace = process_trace(root, analysis_results)
    print(f"{terminal_colors.OKGREEN}[Trace processed]{terminal_colors.ENDC}")


    for run in ptrace:
        print("------------------------------")
        print(f"| RUN {run.run_id} start:{hex(run.start)} |")
        print("------------------------------")
        #for instr in run.instruction_list:
            #print(f"Instr: {instr.opcode}")
            #print(instr.steps_active)
        #    if(len(instr.steps_active)>1):
        #        print(instr.to_xml())
        #print(len(run.instruction_list))
        #print(len(run.instruction_list[0].steps_active))
        #print(len(run.instruction_list[3].steps_active))
        #print(len(run.instruction_list[12].steps_active))


    ptrace_xml = '<?xml version="1.0" encoding="UTF-8"?>'
    ptrace_xml += "<data ptrace_version=\"4.0\">\n"

    ptrace_xml += f'<runs name="{executable_name}">\n' #TODO add check for platform to handle backslash types
    for run in ptrace:
        ptrace_xml += run.to_xml()
    ptrace_xml += '</runs>\n'

    ptrace_xml += analysis_results.to_xml()

    ptrace_xml += "</data>\n"


    #check if we can parse the generated xml
    root = ET.fromstring(ptrace_xml)
    n_ptrace = parse_ptrace_xml(root)
    check_ptrace(n_ptrace)
    n_analysis = parse_analysis_xml(root)
    print(list(enumerate(analysis_results.run_start)))
    #print(analysis_results.potential_child_branches)

    save_file_name = f"{output_path}/{executable_name}.ptrace"
    if(os.path.isfile(save_file_name)):
        if(confirm(f"PTrace file [{save_file_name}] already exists. Overwrite? {terminal_colors.OKGREEN}[y/yes]{terminal_colors.ENDC} ")):
            save_file_text(ptrace_xml, save_file_name, True)
        else:
            print(f"{terminal_colors.FAIL}PTrace was not saved{terminal_colors.ENDC}")
    else:
        save_file_text(ptrace_xml, save_file_name, False)
        print(f"{terminal_colors.OKCYAN}Saved ptrace as [{save_file_name}]{terminal_colors.ENDC}")
    return len(ptrace)
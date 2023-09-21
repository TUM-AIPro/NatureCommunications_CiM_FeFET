import sys
from pathlib import Path
import subprocess
from multiprocessing import Process, Value
import ctypes

import argparse
import os
import shutil
import re
import tempfile
import datetime


netlist_suffix = ".sp"
out_folder_name = Path("out")

process_limit = None

move_raw_up = False

def clean_up_in(directory):
    print("Clean up in: {}".format(directory))
    tempfiles_to_delete = [x for x in directory.iterdir() if x.is_file() and ".tmp" in x.suffix]
    for f in tempfiles_to_delete:
        f.unlink()

    

def do_parallel(file_list, p_num, temp_dir, error_counter):
    bucket_dir = temp_dir / "bucket{}".format(p_num)
    out_path = bucket_dir / out_folder_name
    out_path.mkdir(parents=True, exist_ok=True)

    max_len = 10
    sim_time_list = list()

    number_of_files = len(file_list)

    start = datetime.datetime.today()
    for idx, cur_path in enumerate(file_list):
        if len(sim_time_list) == 0:
            print("Process {}: {} of {}".format(p_num, idx+1, number_of_files))
        else:
            accu = datetime.timedelta(0)
            for x in sim_time_list:
                accu += x
            avg_per_sim = accu / len(sim_time_list)
            remaining_time = avg_per_sim * (number_of_files - idx)
            pred_end_time = datetime.datetime.today() + remaining_time
            print("Process {}:\t{} of {}\t| remaining time delta: {}\tETA: {}".format(p_num, idx+1, number_of_files, remaining_time, pred_end_time.strftime("%Y-%m-%d %H:%M:%S")))
        
        sim_result_path = cur_path.parent / out_folder_name
        sim_result_path.mkdir(parents=True, exist_ok=True)

        # start timer
        timer_start = datetime.datetime.today()
        return_code = worker(cur_path, out_path, error_counter)
        if return_code == 0:
            # retrive results and log from temp folder and store it at correct location
            #shutil.move(str(out_path / (cur_path.stem + ".raw")), str(sim_result_path))
            try:
                shutil.move(str(out_path / (cur_path.stem + ".measure")), str(sim_result_path))
            except:
                pass
        shutil.move(str(out_path / (cur_path.stem + ".log")), str(sim_result_path / (cur_path.stem + ".log")))
        # end timer
        timer_end = datetime.datetime.today()
        delta_time = timer_end - timer_start
        if len(sim_time_list) == max_len:
            sim_time_list = sim_time_list[1:] + [delta_time]
        else:
            sim_time_list.append(delta_time)

def worker(simulation_file, out_path, error_counter):
    
    spectre_call_args_list = ["spectre", "+aps", "-outdir", str(out_path), str(simulation_file)]

    print("Will call: {}".format(spectre_call_args_list))
    return_code = 0
    return_code = subprocess.call(spectre_call_args_list, stdout=subprocess.DEVNULL)
    if return_code != 0:
        print("#########")
        print("Error of call: {}".format(spectre_call_args_list))
        print("Returned: '{}'".format(return_code))
        print("#########")
        with error_counter.get_lock():
            error_counter.value += 1
    return return_code
    
def need_for_simulations(cur_path):
    if (cur_path.parent / out_folder_name / (cur_path.stem + ".measure")).is_file():
        return False
    elif cur_path.is_file() and cur_path.suffix == netlist_suffix:
        return True
    return False

def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(data, key=alphanum_key)

def chunks(l, n):
    """Yield n number of striped chunks from l."""
    for i in range(0, n):
        yield l[i::n]
    

def main(main_args):

    parser = argparse.ArgumentParser(description="Inserts the given parameters in the template SPICE netlist and stores the created netlists to the given location.")
    parser.add_argument("root", help="Path to roots where the netlists reside that should be simulated")
    parser.add_argument("--cleanTempFiles", 
                        help="Clean temp files beginning at given location.",
                        nargs=1,
                        metavar=("SEARCH_ROOT"))
    parser.add_argument("--seq",
                        help="Run all the simulations sequential",
                        action="store_true")
    parser.add_argument("--moveRaw",
                       help="Moves the raw folder one up",
                       action="store_true")
    parser.add_argument("--onlyCleanup",
                       help="Moves the raw folder one up",
                       action="store_true")
    parser.add_argument("--procMax",
                        type=int,
                        default=8,
                       help="Maximum number of parallel processes")
    
    args = parser.parse_args(main_args)

    global move_raw_up, process_limit

    root = Path(args.root)
    do_sequential = args.seq
    process_limit = int(args.procMax)
    move_raw_up = args.moveRaw

    start_time = datetime.datetime.today()


    if args.cleanTempFiles:
        clean_up_root = Path(args.cleanTempFiles[0])
        bucket_list = list()
        for r, dir_list, _ in os.walk(clean_up_root):
            for directory in dir_list :
                clean_up_in(Path(r) / directory)
                if directory.startswith("bucket"):
                    bucket_list.append(Path(r) / directory)

        for bucket in bucket_list:
            shutil.rmtree(str(bucket))


    if args.onlyCleanup:
        sys.exit("Done clean up end now")

    for bucket in root.iterdir():


        files_to_simulate = list()
        for r, folder_list, file_list in os.walk(str(bucket)):
            if "out" in folder_list:
                folder_list.remove("out")
            print(r)
            next_root = Path(r)

            files_to_simulate += [next_root / Path(x) for x in sorted_alphanumeric(file_list) if need_for_simulations(next_root / Path(x))]
        
        sorted_files = sorted_alphanumeric([str(x) for x in files_to_simulate])
        files_to_simulate = [Path(x) for x in sorted_files]

        error_counter = Value(ctypes.c_int) 
        error_counter.value = 0

        if do_sequential:
            for idx, work_item in enumerate(files_to_simulate):
                print("{} of {}".format(idx, len(files_to_simulate)))
                out_path = work_item.parent / out_folder_name 
                worker(work_item, out_path, error_counter)
                
        else:
            buckets_of_files = chunks(files_to_simulate, process_limit)
            with tempfile.TemporaryDirectory() as tmpdirname:
                print(tmpdirname)
                temp_dir_path = Path(tmpdirname)
                proc_list = [Process(target=do_parallel, args=(file_list, p_num, temp_dir_path, error_counter)) for p_num, file_list in enumerate(buckets_of_files)]
                for proc in proc_list:
                    proc.start()
                
                for p_num, proc in enumerate(proc_list):
                    proc.join()
                print("Simulations are done, will now exit temp folder and delete it")

                

        print()
        print("done :)")
        print(f"Errors: {error_counter.value}")
        print("Time elapsed: {}".format(datetime.datetime.today() - start_time))


######################################################
# End of file to ensure it can be executed as script #
######################################################

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)



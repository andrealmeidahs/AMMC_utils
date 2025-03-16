import os
import re
import logging

import numpy as np
import pandas as pd

def int_or_float_or_str(x):
    """
    Converts the input to the first type that works, either:
    - int
    - float
    - string
    (in order of preference)
    """
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            return x

def read_dat(dat_file):
    """
    Reads a generic dat file.

    In general, dat files have a summary line in the last row.
    This is removed if unnamed columns are found.

    Column names are left unchanged
    """
    dfdat = pd.read_csv(dat_file,delimiter="\t")
    # Unnamed columns indicate a multi-run dat file with a last row containing stats
    if any(dfdat.columns.str.match(r"^Unnamed")):
        logging.warning("Removing last line of dat file")
        dfdat = dfdat.iloc[:-1]

    dfdat = dfdat.loc[:,~dfdat.columns.str.match(r"^Unnamed")]
    
    dfdat.loc[:,"run_path"] = os.path.splitext(os.path.split(dat_file)[-1])[0]
    
    return dfdat

def find_empty_line_no(f):
    """
    Find the first empty line number in a text file
    """
    lno=0
    with open(f,"r") as fid:
        for line in fid:
            if len(line) < 2:
                return lno
            lno += 1

def read_multi_run_log_single_file(filename):
    with open(filename,"r") as f:
        log_lines=[]
        dfs=[]
        current_repl = 0
        for line in f:
            if line[0] == '#':
                #print(line)
                m = re.match(r'^.*SCENARIO\s+(\d+)\s+-\s+REPLICATION\s+(\d+).*',line)
                if m:
                    scenario, repl = m.groups()
                if len(log_lines) > 0:
                    df = pd.DataFrame(log_lines[1:],columns=log_lines[0])
                    df["Scenario"] = int(scenario)
                    df["Run"] = int(current_repl)
                    dfs.append(df)
                current_repl = repl
                log_lines=[]


            else:
                els = line.strip('\n').split('\t')
                if len(els) > 1:
                    log_lines.append([int_or_float_or_str(x) for x in els])
        if len(log_lines) > 0:
            df = pd.DataFrame(log_lines[1:],columns=log_lines[0])
            df["Scenario"] = int(scenario)
            df["Run"] = int(current_repl)
            dfs.append(df)

    return pd.concat(dfs[1:])

def find_files_re(root_path, pattern):
    file_list = []
    for proot, dirs, files in os.walk(root_path):
        for f in files:
            if re.match(pattern, f):
                file_list.append(os.path.join(proot,f))
    return file_list

def read_threaded_multi_run_log(run_root, log_element):
    
    patt = r".*"+re.escape(log_element)+r"-s(\d+)r(\d+)\.log"
    files = find_files_re(run_root+"/Outputs", patt)
    
    dfs = []

    for f in files:
        lno = find_empty_line_no(f)
        print(lno, f)
        start_row = lno+1
        m = re.match(patt, f)
        scenario = int(m.groups()[0])
        run = int(m.groups()[1])
        df = pd.read_csv(f,skiprows=start_row,delimiter="\t")
        df.rename(columns=lambda x:x.replace("this.","").replace("/1[h]","_hrs"),inplace=True)
        df["Run"] = run
        df["Scenario"] = scenario

        dfs.append(df)
    
    if len(dfs)>0:
        return pd.concat(dfs)

def read_multi_run_log(run_root, log_element):
    df = read_threaded_multi_run_log(run_root, log_element)
    if df is not None:
        return df
    dfs = []
    for proot, dirs, files in os.walk(os.path.join(run_root,"Outputs")):
        for f in files:
            if re.match(r".*"+re.escape(log_element)+"\.log", f):
                log_fn = os.path.join(proot, f)
                dfs.append(read_multi_run_log_single_file(log_fn))
    return pd.concat(dfs)
        

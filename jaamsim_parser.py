import re
import os
import sys
import argparse
import collections.abc

def deep_update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = deep_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Jaamsim file to parse")
    return parser.parse_args()

class JaamsimParser(object):
    def __init__(self, filename):
        self.struct = {}
        self.open_brackets = 0
        self.open_quote = False
        self.comment = ""
        self.open_comment = False
        self.current_file = filename
        self.current_line = 0
        self.current_col = 0
        self.el_col = 0
        self.current_els = []

    def wrap_element(self, el):
        return {"contents": el.strip(),
                    "comment": self.comment,
                    "line": self.current_line,
                    "column": self.el_col,
                    "file": self.current_file}

    def parse_line(self, s):
        parent_el = self.current_els
        for nb in range(self.open_brackets):
            parent_el = parent_el[-1]
        cur_el = ""
        for chno, c in enumerate(s):
            if c == "#" and not self.open_quote:
                self.open_comment = not self.open_comment
                self.comment = s[chno+1:]
                break
            if not self.open_comment:
                if (c == '{') and not self.open_quote:
                    self.open_brackets += 1
                    parent_el.append([])
                    parent_el = parent_el[-1]
                elif (c == '}') and not self.open_quote:
                    #sys.stderr.write(f"Reducing n brackets to {n_brackets}\n")
                    self. open_brackets -= 1
                    # sys.stderr.write(f"el: {cur_el}\nparent: {parent_el}\ngparent: {grandparent_el}\n")
                    if len(cur_el)>0:
                        parent_el.append(self.wrap_element(cur_el))
                    # el = parent_el.copy()
                    parent_el = self.current_els
                    for nb in range(self.open_brackets):
                        parent_el = parent_el[-1]
                    
                    # parent_el.append(el)
                    cur_el = ""
                elif c == "'":
                    self.open_quote = not self.open_quote
                elif (c == ' ' or c == '\t' or c == '\n') and not self.open_quote:
                    if len(cur_el)>0:
                        parent_el.append(self.wrap_element(cur_el))
                    cur_el = ""
                else:
                    cur_el += c
            
        if self.open_brackets < 1:
            if len(self.current_els) > 0:
                obj = self.current_els[0]
                try:
                    self.struct[obj]
                except KeyError:
                    self.struct[obj] = {}
                for ii in range(1,len(self.current_els),2):
                    self.struct[obj][self.current_els[ii]] = self.current_els[ii+1]
            self.current_els = []
                    
        self.open_comment = False
        self.comment = ""
        self.current_line += 1
        self.current_col = 0

    def parse_file(self,  includes=False):
        base_path, root_file = os.path.split(filename)
    
        with open(filename, "r") as f:
            for line in f:
                sys.stderr.write(line+'\n')
                parts = line.strip().split()
                if len(parts)>0 and parts[0].lower() == "include":
                    incfile = os.path.join(base_path, parts[1].strip("'"))
                    el_inc = parse_jaamsim(incfile, includes=True)
                    deep_update(self.struct, el_inc)
                    continue
                self.parse_line(line)
                        #sys.stderr.write(f"{el_dict[obj]}\n")
                    
                if self.open_brackets < 0:
                    sys.stderr.write("Unmatched brackets")
                # else:
                    # sys.stderr.write(f"{n_brackets},{in_quote}\n")
                #     sys.stderr.write("Unfinished line")
                #     sys.stderr.write(buffer)

        return self.struct

def parse_jaamsim(filename, includes=True):
    parser = JaamsimParser("filename")
    parser.parse_file(includes=True)
    return parser.sturct


if __name__ == "__main__":
    args = parse_args()
    filename = args.filename
    els = parse_jaamsim(filename)
    # for obj, attrs in els.items():
    #     print(obj)
    #     for attr, val in attrs.items():
    #         print("  "+attr+": "+str(val))
            # try:
            # except TypeError:
            #     print("!!"+obj+" -- "+attr)
        


    

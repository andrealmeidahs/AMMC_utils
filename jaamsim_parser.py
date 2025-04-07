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

def parse_line(s, prev_parts=[], n_brackets=0, in_quote=False, in_comment=False):

    els = prev_parts
    parent_el = els
    for nb in range(n_brackets):
        parent_el = parent_el[-1]
    cur_el = ""
    comment = None
    for chno, c in enumerate(s):
        if c == "#" and not in_quote:
            in_comment = True
            comment = s[chno+1:]
            break
        if not in_comment:
            if (c == '{') and not in_quote:
                n_brackets += 1
                parent_el.append([])
                parent_el = parent_el[-1]
            elif (c == '}') and not in_quote:
                #sys.stderr.write(f"Reducing n brackets to {n_brackets}\n")
                n_brackets -= 1
                # sys.stderr.write(f"el: {cur_el}\nparent: {parent_el}\ngparent: {grandparent_el}\n")
                if len(cur_el)>0:
                    el_compl = {"contents":cur_el.strip(),
                                "comment": comment,
                                "file": "",}
                    parent_el.append(cur_el.strip())
                # el = parent_el.copy()
                parent_el = els
                for nb in range(n_brackets):
                    parent_el = parent_el[-1]
                # parent_el.append(el)
                cur_el = ""
            elif c == "'":
                in_quote = not in_quote
            elif (c == ' ' or c == '\t' or c == '\n') and not in_quote:
                if len(cur_el)>0:
                    parent_el.append(cur_el.strip())
                cur_el = ""
            else:
                cur_el += c
            
    return els, n_brackets, in_quote, in_comment

def parse_jaamsim(filename, includes=False):

    base_path, root_file = os.path.split(filename)
    
    buffer = ""
    el_list = []
    el_dict = {}

    n_brackets = 0
    in_comment = False
    in_quote = False
    els = []
    with open(filename, "r") as f:
        for line in f:
            sys.stderr.write(line+'\n')
            parts = line.strip().split()
            if len(parts)>0 and parts[0].lower() == "include":
                incfile = os.path.join(base_path, parts[1].strip("'"))
                el_inc = parse_jaamsim(incfile, includes=True)
                deep_update(el_dict, el_inc)
                el_list.extend(el_inc)
                continue
            (els, n_brackets,
             in_quote ,
             in_comment) = parse_line(line,
                                      prev_parts=els,
                                      n_brackets=n_brackets,
                                      in_quote=in_quote,
                                      in_comment=in_comment)
            in_comment = False
            if n_brackets < 1:
                if len(els) > 0:
                    sys.stderr.write(f"> {buffer}\n")
                    el_list.append(els)
                    obj = els[0]
                    try:
                        el_dict[obj]
                    except KeyError:
                        el_dict[obj] = {}
                    for ii in range(1,len(els),2):
                        el_dict[obj][els[ii]] = els[ii+1]
                    #sys.stderr.write(f"{el_dict[obj]}\n")
                    
                if n_brackets < 0:
                    sys.stderr.write("Unmatched brackets")
                n_brackets = 0
                els = []
            # else:
                # sys.stderr.write(f"{n_brackets},{in_quote}\n")
            #     sys.stderr.write("Unfinished line")
            #     sys.stderr.write(buffer)

    return el_dict


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
        


    

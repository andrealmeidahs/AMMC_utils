import re
import sys
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Jaamsim file to parse")
    return parser.parse_args()

def parse_line(s, n_brackets=0, in_quote=False, in_comment=False):

    els = []
    parent_el = els
    cur_el = ""
    for c in s:
        if c == "#" and not in_quote:
            in_comment = True
        if not in_comment:
            if (c == '{') and not in_quote:
                n_brackets += 1
                parent_el.append([])
                grandparent_el = parent_el
                parent_el = parent_el[-1]
            elif (c == '}') and not in_quote:
                #sys.stderr.write(f"Reducing n brackets to {n_brackets}\n")
                n_brackets -= 1
                # sys.stderr.write(f"el: {cur_el}\nparent: {parent_el}\ngparent: {grandparent_el}\n")
                if len(cur_el)>0:
                    parent_el.append(cur_el)
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
                    parent_el.append(cur_el)
                cur_el = ""
            elif not in_comment:
                cur_el += c
            
            
    return els, n_brackets, in_quote, in_comment

def parse_jaamsim(filename, includes=False):
    buffer = ""
    el_list = []

    n_brackets = 0
    in_comment = False
    in_quote = False
    with open(filename, "r") as f:
        for line in f:
            buffer += line
            (els, n_brackets,
             in_quote ,
             in_comment) = parse_line(buffer,
                                      n_brackets=0,
                                      in_quote=False,
                                      in_comment=in_comment)
            in_comment = False
            if n_brackets < 1:
                if len(els) > 0:
                    sys.stderr.write(f"> {buffer}\n")
                    sys.stderr.write(f"{els}\n")
                    el_list.append(els)
                buffer = ""
                if n_brackets < 0:
                    sys.stderr.write("Unmatched brackets")
                n_brackets = 0
            # else:
                # sys.stderr.write(f"{n_brackets},{in_quote}\n")
            #     sys.stderr.write("Unfinished line")
            #     sys.stderr.write(buffer)

            if line[:6] == "include" and includes:
                # write logic to include file
                continue
    return el_list


if __name__ == "__main__":
    args = parse_args()
    filename = args.filename
    els = parse_jaamsim(filename)
    for el in els:
        print(el)


    

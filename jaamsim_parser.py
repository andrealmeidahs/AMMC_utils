import re
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Jaamsim file to parse")
    return parser.parse_args()

def parse_statement(s):
    n_brackets = 0
    in_quote = False

    els = []
    cur_el = ""
    for c in s:
        if c == '{' and not in_quote:
            n_brackets += 1
        elif c == '}' and not in_quote:
            n_brackets -= 1
        elif c == "'":
            in_quote = not in_quote
        elif c == ' ' or c == '\t':
            els += cur_el
            cur_el = ""
        else:
            cur_el += c 
    return els

def parse_line(line, cur_statement=""):
    cur_statement += line.strip()
    if re.match(r"^include", cur_statement):
        type = "inc"
        els = re.match(r"^include\s+(.*)$", cur_statement).groups()[0]
        return type, els
    elif re.match(l,"^Define"):
        type = "def"
        els = re.match(r"^Define\s+(.*)$", cur_statement).groups()[0]
        return type, els
    elif re.match(l,"^RecordEdits"):
        type = "st"
        return 
    else:
        type = ""
        els = cur_statement
    

def parse_jaamsim(filename, includes=False):
    with open(filename, "r") as f:
        for line in f:
            parts, n_open_brackets = parse_line(line)
            if n_open_brackets == 0:
                els = parse_parts(parts)
            if line[:6] == "include":
                # write logic to include file
                continue
            





if __name__ == "__main__":
    args = parse_args()
    filename = args.filename
    parse_jaamsim(filename)


    
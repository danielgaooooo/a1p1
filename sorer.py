#!/usr/bin/env python3
import argparse
import enum
import re
import os
import pickle

"""
Data Adapter for SoR files
Authors: Daniel Guo (gao.d@husky.neu.edu) and Brian Yeung (yeung.bri@husky.neu.edu)
"""

CHUNK_SIZE = 100000 # number of rows to pickle to memory at a time
chunk_count = 0
parser = argparse.ArgumentParser()

# Attribution: From - https://stackoverflow.com/a/14117511/12602247 At - 1/23/20 10:57 AM
# Confirms that the value is positive, and refuses it if it is not
def check_positive(val):
    int_val = int(val)
    if int_val < 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % val)
    return int_val

# Confirms that every value in a list of integers is positive
def check_pos_list(vals):
    for i in vals:
        if int(i) < 0:
            raise argparse.ArgumentTypeError("%s is an invalid positive int value" % i)
    return vals

# Mandatory args
requiredNamed = parser.add_argument_group('required named arguments')
requiredNamed.add_argument('-f', help='Input file name', required=True, metavar="filename")

# Optional args
parser.add_argument("-from", help="Starting postion in the file (in bytes)", 
    metavar="start_idx", dest="from_offset", type=check_positive)
parser.add_argument("-len", help="Number of bytes to read", 
    metavar="length", type=check_positive)

# Mutually exclusive args
group = parser.add_mutually_exclusive_group()
group.add_argument("-print_col_type", help="Print type of column", 
    metavar="column_idx", type=check_positive)
group.add_argument("-print_col_idx", help="Print value at column, offset", 
    nargs=2, metavar=("column_idx", "offset_idx"), type=check_pos_list)
group.add_argument("-is_missing_idx", help="Is there a missing in the specified column offset", 
    nargs=2, metavar=("column_idx", "offset_idx"), type=check_pos_list)
args = parser.parse_args()

num_cols = 0
schema = []
columns = []

# Possible column types - missing fields are denoted as MISSING
class Type(enum.Enum):
    MISSING = -1
    BOOL = 0
    INT = 1
    FLOAT = 2
    STRING = 3

    def __str__(self):
        return self.name

# size of the sor file we are processing
filesize = os.stat(args.f).st_size

# various regex that are useful for parsing fields
missing_re = re.compile(r"^\s*$")
bool_re = re.compile(r"^\s*[01]\s*$")
int_re = re.compile(r"^\s*[+-]?\d*\s*$")
float_re = re.compile(r"\s*[+-]?\d*\.\d*\s*")
string_re = re.compile(r"\s*\"[^\"]*\"\s*")
no_quote_re = re.compile(r"\s*[^\x00-\x7F]*\s*")
field_delimiter_re = re.compile(r"<([^<>]*)>") 

# Returns inferred type of the value from regex parsing
def infer_type(val):
    if missing_re.findall(val):
        return Type.MISSING
    elif bool_re.findall(val):
        return Type.BOOL
    elif int_re.findall(val):
        return Type.INT
    elif float_re.findall(val):
        return Type.FLOAT
    elif string_re.findall(val) or no_quote_re.findall(val):
        return Type.STRING
    else:
        return None # value is invalid

# Runs inference on each field and checks for longest row.
# Infers type of each field, and updates schema appropriately
def parse_line(values):
    global num_cols
    if (len(values) > num_cols):
        num_cols = len(values)
    # infer type from values to make schema
    for idx, val in enumerate(values):
        inferred_type = infer_type(val)
        if len(schema) < idx + 1:
            schema.append(inferred_type)
        
        cur_type = schema[idx] 
        # if in a super group replace what is in schema
        if cur_type and inferred_type and cur_type.value < inferred_type.value:
            schema[idx] = inferred_type

# Infers the schema from the first 500 lines of the sor file
def infer_schema():
    global columns
    offset = (args.from_offset, 0)[args.from_offset == None] 
    length = (args.len, os.stat(args.f).st_size)[args.len == None]
    with open(args.f, "r") as f:
        f.seek(offset)
        bytes_read = 0
        if (offset > 0): # don't discard if offset is set to 0
            line = f.readline() # discard up to next new line character
            bytes_read = len(line)
        count = 0
        line = f.readline()
        while(line and bytes_read <= length and count < 500):
            bytes_read += len(line)
            # skip if on last line and length is defined
            if (args.len != None and bytes_read > length):
                break

            # Inferring the schema
            values = field_delimiter_re.findall(line)
            parse_line(values)

            line = f.readline()
            count += 1
    columns = [[] for i in range(len(schema))]

# Checks if this line is valid sor. If not, discard.
def valid_row(values):
    global num_cols
    global schema
    # Split by field delimiters
    for i in range(len(values)):
        val_type = infer_type(values[i])
        # If there are non-missing fields past num_col, row is invalid
        if (i + 1) > num_cols:
            if val_type != Type.MISSING:
                return False
        else:
            # check field conforms to the schema, subgroups are okay
            if val_type.value > schema[i].value:
                return False
    return True

# Returns tuples of inferred type of the value and the value
def get_field(target_column, target_offset):
    global columns
    # if current chunk contains offset, return, else go unpickle the correct chunk file
    correct_columns = None
    if (target_offset >= chunk_count * CHUNK_SIZE):
        correct_columns = columns
    else:
        correct_chunk = int(target_offset / CHUNK_SIZE)
        with open('chunk_' + str(correct_chunk), 'rb') as f:
            correct_columns = pickle.load(f)

    val = correct_columns[target_column][target_offset % CHUNK_SIZE]
    val_type = schema[target_column]
    if val_type == Type.STRING and val[0] != '"':
        val = '"' + val + '"'
    return (val_type, val)

# adds the row of values to the global list of columns
def update_columns(values):
    global columns, chunk_count
    if (len(columns[0]) >= CHUNK_SIZE):
        # pickle columns
        with open('chunk_' + str(chunk_count), 'wb') as f:
            pickle.dump(columns, f)
        chunk_count += 1
        # reset columns
        columns = [[] for i in range(len(schema))]
    
    num_values = len(values)
    # add each value to the column grid
    for i in range(num_values):
        columns[i].append(values[i])
    # for every missing value, add None to indicate it's missing
    for i in range(len(schema) - num_values):
        columns[i + num_values].append(None)

# Parse data file into columnar format
def columnar():
    offset = (args.from_offset, 0)[args.from_offset == None] 
    length = (args.len, filesize)[args.len == None]
    with open(args.f, "r") as f:
        f.seek(offset)
        bytes_read = 0
        if (offset > 0): # don't discard if offset is set to 0
            line = f.readline() # discard up to next new line character
            bytes_read = len(line)
        count = 0
        line = f.readline()
        while(line and bytes_read < length):
            bytes_read += len(line)
            # skip if on last line and length is defined
            values = field_delimiter_re.findall(line)
            if (args.len != None and bytes_read >= length):
                break
            if valid_row(values):
                count += 1
                update_columns(values)
            line = f.readline()

# Cleanly exit after printing error message
def error_exit(error_msg):
    print(error_msg)
    exit(1)

def main():
    global columns, chunk_count, CHUNK_SIZE
    # Check file exists
    try:
        f = open(args.f)
    except IOError:
        error_exit("File cannot be opened")
    finally:
        f.close()

    if (args.from_offset and args.from_offset > filesize):
        error_exit("From index larger than filesize")

    infer_schema()

    if (args.print_col_type != None):
        if (args.print_col_type < 0 or args.print_col_type >= len(schema)):
            error_exit('Column index out of range')
        print(schema[args.print_col_type])
    elif (args.print_col_idx != None or args.is_missing_idx != None):
        target = (args.is_missing_idx, args.print_col_idx)[args.is_missing_idx == None] 
        target_column = int(target[0])
        target_offset = int(target[1])

        columnar()
        if (target_column < 0 or target_column >= len(schema)):
            error_exit("Column index out of range")

        if (target_offset < 0 or target_offset >= chunk_count * CHUNK_SIZE + len(columns[0])):
            error_exit("Offset index out of range")

        result = get_field(target_column, target_offset)
        if (args.print_col_idx):
            print(result[1])
        else:
            if (result[0] == Type.MISSING):
                print(1)
            else:
                print(0)
if __name__ == "__main__":
    main()
# Sorer

Sorer is a data adapter for schema on read data files. 

A row is delimited by a new line character
A field is surrounded by angle brackets
Longest row in the first 500 lines is the number of fields in the schema
Schema is inferred from these first 500 lines

A String is a double quoted value or sequence of characters without spaces
A Float can lead with a sign (+/-) followed by sequence of numbers possibily with a dot somewhere in the middle
An Integer can lead with a sign (+/-) followed by sequence of numbers
A Bool is a 0 or a 1

If there is a String in the column, the column is of type String
Else if there is a Float in the column, the column is of type Float
Else if there is a value with a leading sign or value greater than 1, the column is of type Int
Else the column is of type Bool

Assume columns are left aligned, missing columns can only be at the end of rows
All rows that don't follow the schema are considered invalid rows, and are discarded (not counted in idx for cli args)

## Installation

Requires Python3

## Usage
Returns column inferred type:
-print_col_type takes in column index

Returns 0 (false) or 1 (true) if value is missing:
-is_missing_idx requires column index and row offset from beginning row (could be from middle of file)

Returns value at location
-print_col_idx requires column index and row offset

Examples
```
# Return help information
$ ./sorer.py -h

$ ./sorer.py -f data.sor -print_col_type 1
INT

$ ./sorer.py -f data.sor -len 100 -print_col_type 2
STRING

$ ./sorer.py -f data.sor -from 10 -print_col_type 0
BOOL

$ ./sorer -f "data.sor" -from 0 -len 100 -print_col_type 0
BOOL

$ ./sorer -f "data.sor" -is_missing_idx 2 0
0

$ ./sorer -f "data.sor" -print_col_idx 2 0
"hi"

$ ./sorer -f "data.sor" -print_col_idx 1 0
12
```
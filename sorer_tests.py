#!/usr/bin/env python3

import subprocess
from collections import namedtuple

base_cmd = ['python3', 'sorer.py', '-f', 'temp_test.sor']

Test = namedtuple('Test', 'cmd data expected')

# Test Suites
from_suite = [
    Test(['-from', '1', '-print_col_type', '0'], '<0> <1> <hi>\n<!^%&*$(#)!> <1> <hi>\n', 'STRING'),
    Test(['-from', '12', '-print_col_type', '0'], '<0> <1> <hi>\n<ABCD> <1> <hi>\n', 'STRING'),
    Test(['-from', '11', '-print_col_type', '0'], '<0> <1> <hi>\n<ABCD> <1> <hi>\n', 'STRING'),
    Test(['-from', '13', '-print_col_type', '0'], '<0> <1> <hi>\n<ABCD> <1> <hi>\n<0><asdf><>', 'BOOL'),
    Test(['-from', '16', '-print_col_type', '0'], '<0> <1> <hi>\n<ABCD> <1> <hi>\n<0><asdf><>', 'BOOL'),
    Test(['-from', '100', '-print_col_type', '0'], '<0> <1> <hi>\n<ABCD> <1> <hi>\n<0><asdf><>', 'From index larger than filesize'),
]

len_suite = [
    Test(['-len', '12', '-print_col_type', '0'], '<0> <1> <hi>\n<ABCD> <1> <hi>\n<0><asdf><>', 'Column index out of range'),
    Test(['-len', '13', '-print_col_type', '0'], '<0> <1> <hi>\n<ABCD> <1> <hi>\n<0><asdf><>', 'BOOL'),
    Test(['-len', '14', '-print_col_type', '0'], '<0> <1> <hi>\n<ABCD> <1> <hi>\n<0><asdf><>', 'BOOL'),
    Test(['-len', '16', '-print_col_idx', '1', '0'], '<0> <1> <hi>\n<ABCD> <1> <hi>\n<0><asdf><>', '1'),
]

field_value_suite = [
    Test(['-print_col_type', '0'], '<0> <1> <hi>\n', 'BOOL'),
    Test(['-print_col_type', '0'], '<0> <0> <hi>\n', 'BOOL'),
    Test(['-print_col_type', '0'], '<0> <1> <hi>\n<-1> <1> <hi>\n', 'INT'),
    Test(['-print_col_type', '0'], '<0> <1> <hi>\n<-0> <1> <hi>\n', 'INT'),
    Test(['-print_col_type', '0'], '<0> <1> <hi>\n<+0> <1> <hi>\n', 'INT'),
    Test(['-print_col_type', '0'], '<0> <1> <hi>\n<10> <1> <hi>\n', 'INT'),
    Test(['-print_col_type', '0'], '<0> <1> <hi>\n<+10> <1> <hi>\n', 'INT'),
    Test(['-print_col_type', '0'], '<0> <1> <hi>\n<-10> <1> <hi>\n', 'INT'),
    Test(['-print_col_type', '0'], '<0> <1> <hi>\n<10.2> <1> <hi>\n', 'FLOAT'),
    Test(['-print_col_type', '0'], '<0> <1> <hi>\n<+10.2> <1> <hi>\n', 'FLOAT'),
    Test(['-print_col_type', '0'], '<0> <1> <hi>\n<-10.2> <1> <hi>\n', 'FLOAT'),
    Test(['-print_col_type', '0'], '<0> <1> <hi>\n<0.2> <1> <hi>\n', 'FLOAT'),
    Test(['-print_col_type', '0'], '<0> <1> <hi>\n<.2> <1> <hi>\n', 'FLOAT'),
    Test(['-print_col_type', '0'], '<0> <1> <hi>\n<0.> <1> <hi>\n', 'FLOAT'),
    Test(['-print_col_type', '0'], '<0> <1> <hi>\n<"hi"> <1> <hi>\n', 'STRING'),
    Test(['-print_col_type', '0'], '<0> <1> <hi>\n<asdkfjklasn> <1> <hi>\n', 'STRING'),
    Test(['-print_col_type', '0'], '<0> <1> <hi>\n<"           "> <1> <hi>\n', 'STRING'),
    Test(['-print_col_type', '0'], '<0> <1> <hi>\n<   "           "   > <1> <hi>\n', 'STRING'),
    Test(['-print_col_type', '0'], '<0> <1> <hi>\n<"!@#$%^&*()"> <1> <hi>\n', 'STRING'),
    Test(['-print_col_type', '0'], '<0> <1> <hi>\n<!^%&*$(#)!> <1> <hi>\n', 'STRING'),
]

is_missing_suite = [
    Test(['-is_missing_idx', '0', '0'], '<>', '1'),
    Test(['-is_missing_idx', '0', '0'], '<      >', '1'),
    Test(['-is_missing_idx', '2', '0'], '<0><asdf><>', '1'),
    Test(['-is_missing_idx', '1', '0'], '<0><asdf><>', '0'),
    Test(['-is_missing_idx', '2', '1'], '<0><asdf><>\n<><><>', '1'),
    Test(['-is_missing_idx', '0', '1'], '<>', 'Offset index out of range'),
]

print_col_idx_suite = [
    Test(['-print_col_idx', '0', '0'], '<0><12.0><asdf><"asdfasdf   ">', '0'),
    Test(['-print_col_idx', '0', '0'], '<1><12.0><asdf><"asdfasdf   ">', '1'),
    Test(['-print_col_idx', '0', '0'], '<1010100><12.0><asdf><"asdfasdf   ">', '1010100'),
    Test(['-print_col_idx', '0', '0'], '<+1010100><12.0><asdf><"asdfasdf   ">', '+1010100'),
    Test(['-print_col_idx', '0', '0'], '<-1010100><12.0><asdf><"asdfasdf   ">', '-1010100'),
    Test(['-print_col_idx', '1', '0'], '<0><12.0><asdf><"asdfasdf   ">', '12.0'),
    Test(['-print_col_idx', '1', '0'], '<0><+12.0><asdf><"asdfasdf   ">', '+12.0'),
    Test(['-print_col_idx', '1', '0'], '<0><-12.0><asdf><"asdfasdf   ">', '-12.0'),
    Test(['-print_col_idx', '1', '0'], '<0><2.><asdf><"asdfasdf   ">', '2.'),
    Test(['-print_col_idx', '1', '0'], '<0><.2><asdf><"asdfasdf   ">', '.2'),
    Test(['-print_col_idx', '2', '0'], '<0><12.0><asdf><"asdfasdf   ">', '"asdf"'),
    Test(['-print_col_idx', '2', '0'], '<0><12.0><!@#$%^&*()><"asdfasdf   ">', '"!@#$%^&*()"'),
    Test(['-print_col_idx', '3', '0'], '<0><12.0><asdf><"asdfasdf   ">', '"asdfasdf   "'),
    Test(['-print_col_idx', '3', '0'], '<0><12.0><asdf><>', ''),
    Test(['-print_col_idx', '0', '1'], '<>', 'Offset index out of range'),
    Test(['-print_col_idx', '1', '0'], '<>', 'Column index out of range'),
]

schema_update_suite = [
    Test(['-print_col_type', '0'], 
    '<0>        <1> <hi>  \n'
    '<0>        <1> <hi>  \n'
    '<0>        <1> < hi> \n'
    '< 0>       <1> <hi>  \n'
    '<  "hey" > <1> <hi>  \n', 'STRING'),
    Test(['-print_col_type', '1'], 
    '<0> <1> <hi>\n'
    '<0> <1> <hi>\n'
    '<0> <1> < hi>\n'
    '< 0> < 1> <hi>\n'
    '<  "hey hey hey!" > <1.> <hi>\n', 'FLOAT'),
    Test(['-print_col_type', '2'], 
    '<0> <1> <hi>\n'
    '<0> <1> <4.4>\n'
    '<0> <1> < 2>\n'
    '< 0> < 1> <1>\n'
    '<  "hey hey hey!" > <1.> <hi>\n', 'STRING'),
    Test(['-print_col_type', '3'], 
    '<0> <1> <hi>\n'
    '<0> <1> <4.4> <>\n'
    '<0> <1> < 2>\n'
    '< 0> < 1> <1> <> \n'
    '<  "hey hey hey!" > <1.> <hi> <0>\n', 'BOOL')
]

test_suites = []
test_suites.append(("from Suite", from_suite))
test_suites.append(("len Suite", len_suite))
test_suites.append(("print_col_type Suite", field_value_suite))
test_suites.append(("is_missing_idx Suite", is_missing_suite))
test_suites.append(("print_col_idx Suite", print_col_idx_suite))
test_suites.append(("schema update Suite", schema_update_suite))


for test_suite in test_suites:
    test_suite_name = test_suite[0]
    tests = test_suite[1]
    
    for idx, test in enumerate(tests):
        expected = test.expected

        with open('temp_test.sor', 'w') as f:
            f.write(test.data)

        result = subprocess.run(base_cmd + test.cmd, stdout=subprocess.PIPE)
        actual = result.stdout.decode('utf-8')

        if expected.strip() != actual.strip():
            print(f'Test {idx} in {test_suite_name} failed: expected "{expected}", got {actual.strip()}')

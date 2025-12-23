#!/usr/bin/env python

from seqmagick2 import fileformat

extension_map = fileformat.EXTENSION_TO_TYPE
items = sorted(extension_map.items())

max_key_length = max((len('Extension'), max(len(k) for k in extension_map.keys())))
max_val_length = max((len('Format'), max(len(v) for v in extension_map.values())))
format_string = '{0:' + str(max_key_length) + 's} {1:' + str(max_val_length) + 's}'

with open('extensions.rst', 'w') as fp:
    def print_row(k, v):
        print(format_string.format(k, v), file=fp)
    print_row('=' * max_key_length, '=' * max_val_length)
    print_row('Extension', 'Format')
    print_row('=' * max_key_length, '=' * max_val_length)
    for k, v in items:
        print_row(k, v)
    print_row('=' * max_key_length, '=' * max_val_length)
    print('', file=fp)

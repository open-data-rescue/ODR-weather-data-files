# -*- coding: utf-8 -*-

import io
import pandas as pd

def read_file(file_name):
    """Load the contents of the specified file.

    Args:
        file_name (:obj:`str`): File (or 'open'able object)

    Returns:
        :obj:`dict`: Data as key:value pairs.

    Raises:
        IOError: Not a readable SEF file.

    |
    """

    f = io.open(file_name, 'r')
    # Check that it's a SEF file and get the version
    l = f.readline().rstrip()
    if l[0:4] != 'SEF\t':
        raise IOError("%s does not look like a SEF file" % file_name)
    version = l.split('\t')[1]
    iversion = [int(x) for x in version.split('.')]
    if iversion[1] > 0 or iversion[2] > 0:
        raise IOError("SEF versions > 0.0 are not supported")
    result = {'SEF': version}
    # Read in the header rows
    for row in range(10):
        header = f.readline().rstrip().split('\t')
        try:
            result[header[0]] = header[1]
        except IndexError:
            result[header[0]] = None
    if 'Meta' in result.keys():
        if result['Meta'] is not None:
            result['Meta'] = result['Meta'].split(',')
    f.close()
    # Read in the data table
    o = pd.read_csv(file_name, sep='\t', index_col= False, skiprows=12)
    o['Meta'] = o['Meta'].map(lambda x: x.split(','), na_action='ignore')
    result['Data'] = o
    return result


input_file = "filename.tsv"
df = read_file(input_file)

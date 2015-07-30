# -*- coding: utf-8 -*-

from __future__ import print_function

import os, sys
import numpy as np
from ccdb import AlchemyProvider as CCDBProvider

from datetime import datetime

class Bunch(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

# run control parameters
rc = Bunch(
    run = 0,
    runmin = 0,
    runmax = np.inf,
    variation = 'default',
    date_and_time = None,
    connstr = os.environ.get('CCDB_CONNECTION',
              'mysql://clas12reader@clasdb.jlab.org/clas12'),
    comment = '',
    resized_string_dtype = '|S256',
    resized_unicode_dtype = '<U256',
)

def list_tables(connstr = None):
    '''
    returns a list of tables in this CCDB database
    '''
    connstr = rc.connstr if connstr is None else connstr

    # initialize database Provider class to interface with CCDB
    if not hasattr(get_tables, 'provider'):
        get_tables.provider = CCDBProvider()
    provider = get_tables.provider

    # connect to database (MySQL or SQLite)
    if provider.is_connected:
        if provider.connection_string != connstr:
            provider.disconnect()
            provider.connect(connstr)
    else:
        provider.connect(connstr)



def get_table(table_path,
              run           = None,
              variation     = None,
              date_and_time = None,
              connstr       = None ):
    '''
    This function connects to the database using the
    provided connection string and queries for the
    dataset according to table, run, variation and
    date_and_time. This will be a unique set of constants.

    A numpy record array is created and then returned.

    example::

        opts = dict(
            connstr = 'mysql://clas12reader@clasdb.jlab.org/clas12',
            table = '/calibration/ftof/status',
            run = 0,
            variation = 'default',
            date_and_time = datetime.now(),
            )
        data = get_data(**opts)

        # sector of the first three rows
        print data.sector[:3]

        # same as above
        print data[:3].sector

        # sector and panel for the last three rows
        print data[-3:][['sector','panel']]

        # 201st row of the data (indexing from zero)
        print data[200]

    will print out the following::

        [1 1 1]
        [1 1 1]
        [(6, '2') (6, '2') (6, '2')]
        (3, '1a', 21, 0, 0)

    '''
    run           = rc.run           if run           is None else run
    variation     = rc.variation     if variation     is None else variation
    date_and_time = rc.date_and_time if date_and_time is None else date_and_time
    connstr       = rc.connstr       if connstr       is None else connstr

    if date_and_time is None:
        date_and_time = datetime.now()

    # initialize database Provider class to interface with CCDB
    if not hasattr(get_table, 'provider'):
        get_table.provider = CCDBProvider()
    provider = get_table.provider

    # connect to database (MySQL or SQLite)
    if provider.is_connected:
        if provider.connection_string != connstr:
            provider.disconnect()
            provider.connect(connstr)
    else:
        provider.connect(connstr)

    # Get assignments* for this specific data
    # *there should only be one since we
    #  specify run, variation AND date/time
    assignment = provider.get_assignments(table_path,
                             run=run,
                             variation=variation,
                             date_and_time=date_and_time)[0]

    # read in column names and types
    type_table = provider.get_type_table(table_path)
    columns = type_table.columns

    # convert unicode to ascii for the column names
    colnames = [str(c.name) for c in columns]

    # convert type string to Numpy dtype string specifications
    coltypes = []
    for c in columns:
        t = c.type
        if t == 'string':
            t = 'str'
        coltypes.append(str(np.dtype(t)))

    # strings of length zero make no sense. set dtype
    # according to rc.resized_string_dtype
    for i,k in enumerate(coltypes):
        if k == '|S0':
            coltypes[i] = rc.resized_string_dtype
        if k == '<U0':
            coltypes[i] = rc.resized_unicode_dtype

    # get access to the constants themselves
    constant_set = assignment.constant_set

    # get table of data as a numpy 2D array of strings
    strdata = np.array(constant_set.data_table, dtype=str).T

    # create empty numpy record array with the
    # target column names and types
    data = np.recarray(strdata.shape[1],
                       dtype=list(zip(colnames,coltypes)))

    # for each column, read in data and convert to
    # the appropriate type
    for d,n,t in zip(strdata,colnames,coltypes):
        data[n][...] = d.astype(t)

    # return the numpy record array
    return data


def add_table(data,
              table_path,
              runmin        = None,
              runmax        = None,
              variation     = None,
              comment       = None,
              connstr       = None ):
    '''
    This function connects to the database using the
    provided connection string
    '''
    runmin    = rc.runmin    if runmin    is None else runmin
    runmax    = rc.runmax    if runmax    is None else runmax
    variation = rc.variation if variation is None else variation
    comment   = rc.comment   if comment   is None else comment
    connstr   = rc.connstr   if connstr   is None else connstr

    # initialize database Provider class to interface with CCDB
    if not hasattr(add_table, 'provider'):
        add_table.provider = CCDBProvider()
    provider = add_table.provider

    # connect to database (MySQL or SQLite)
    if provider.is_connected:
        if provider.connection_string != connstr:
            provider.disconnect()
            provider.connect(connstr)
    else:
        provider.connect(connstr)

    assignment = provider.create_assignment(
        [list(i) for i in list(data)],
        path = table_path,
        min_run = runmin,
        max_run = runmax,
        variation_name = variation,
        comment = comment)


if __name__ == '__main__':
    ftof_stat = get_table('/calibration/ftof/status')
    print(ftof_stat[:10])

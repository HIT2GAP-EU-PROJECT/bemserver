#!/usr/bin/env python3
#
# * Load an IFC file into the Hit2Gap data model

import sys
import getopt
from h2g_platform_core.basicservices.bim.ifc_import import IfcImport
from h2g_platform_core.database import DBAccessor, init_handlers

ONTO_URL = 'http://h2g-platform-core.nobatek.com:3030/hit2gap/'


def main(argv):
    ifc_file = ''
    try:
        opts, args = getopt.getopt(argv, "h")
    except getopt.GetoptError:
        print('load_ifc.py <ifc_file>')
        sys.exit(2)
    if opts == ['-h'] or len(args) != 1:
        print('load_ifc.py <ifc_file>')
        sys.exit()
    ifc_file = args[0]
    db_accessor = DBAccessor()
    db_accessor.set_handler(init_handlers(url=ONTO_URL))
    ifc_import = IfcImport(ifc_file, db_accessor=db_accessor)
    ifc_import.execute()


if __name__ == "__main__":
    main(sys.argv[1:])

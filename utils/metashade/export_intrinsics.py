# Copyright (C) Microsoft Corporation. All rights reserved.
# This file is distributed under the University of Illinois Open Source License. See LICENSE.TXT for details.

import argparse
import os
import hctdb_instrhelp as hct

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = "Generate Metashade code for HLSL intrinsics from their definitions in DXC"
    )
    parser.add_argument("--metashade-root", help = "Path to the root directory of the Metashade repo")
    args = parser.parse_args()
    
    if not os.path.isdir(args.metashade_root):
        raise NotADirectoryError(args.metashade_root)

    db = hct.get_db_hlsl()
    
    for intr in sorted(db.intrinsics, key=lambda x: x.key):
        if intr.ns != "Intrinsics" or intr.vulkanSpecific:
            continue

        print (intr.name)

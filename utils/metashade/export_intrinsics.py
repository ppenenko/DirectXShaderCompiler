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

    for intr in sorted(db.intrinsics, key = lambda intr: intr.name):
        if (   intr.ns != "Intrinsics"
            or intr.vulkanSpecific
            or intr.hidden
            or len(intr.params) != 2
        ):
            continue

        # This param represents the return value, check the assumption that
        # it's always the first one
        assert(intr.params[0].name == intr.name)

        skip_intr = False
        for param in intr.params:
            if param.component_list not in (
                'LICOMPTYPE_FLOAT_LIKE',
                'LICOMPTYPE_ANY_FLOAT',
                'LICOMPTYPE_FLOAT_DOUBLE'
            ):
                skip_intr = True
                continue
            if param.name == intr.name or intr.hidden:
                if (param.template_list not in ('LITEMPLATE_ANY' 'LITEMPLATE_SCALAR')):
                    skip_intr = True
                    continue
            else:
                # This is the only parameter
                if (param.template_list != 'LITEMPLATE_ANY'):
                    skip_intr = True
                    continue

        if skip_intr:
            continue

        print(intr.name)

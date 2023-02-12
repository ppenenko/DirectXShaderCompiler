# Copyright (C) Microsoft Corporation. All rights reserved.
# This file is distributed under the University of Illinois Open Source License. See LICENSE.TXT for details.

import argparse
import os
import hctdb_instrhelp as hct

def _generate_floatlike_intrinsics(f):
    f.write(
'''# Copyright 2023 Pavlo Penenko
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.\n\n'''
    )

    f.write('class FloatlikeMixin:\n')

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
            if param.name == intr.name:
                if (param.template_list not in
                    ('LITEMPLATE_ANY' 'LITEMPLATE_SCALAR')
                ):
                    skip_intr = True
                    continue
            else:
                # This is the only parameter
                if (param.template_list != 'LITEMPLATE_ANY'):
                    skip_intr = True
                    continue

        if skip_intr:
            continue

        f.write(f'\tdef {intr.name}(self):\n')
        f.write(f'\t\treturn self.__class__( f\'{intr.name}({{self}})\' )\n\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = "Generate Metashade code for HLSL intrinsics from their definitions in DXC"
    )
    parser.add_argument("--metashade-root", help = "Path to the root directory of the Metashade repo")
    args = parser.parse_args()
    
    if not os.path.isdir(args.metashade_root):
        raise NotADirectoryError(args.metashade_root)

    file_name  = os.path.join(args.metashade_root, 'metashade', 'hlsl', 'sm6', 'float_intrinsics.py')
    with open(file_name, 'w') as f:
        _generate_floatlike_intrinsics(f)

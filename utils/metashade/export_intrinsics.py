# Copyright (C) Microsoft Corporation. All rights reserved.
# This file is distributed under the University of Illinois Open Source License. See LICENSE.TXT for details.

import argparse
import os
import hctdb_instrhelp as hct

impl_header = \
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
# limitations under the License.

# ATTENTION! This file has been auto-generated by
# https://github.com/ppenenko/DirectXShaderCompiler/blob/metashade/issues/9/export_intrinsics/utils/metashade/export_intrinsics.py
 
'''

def _generate_intrinsic(intr, impl_file, test_file):
    self_idx = 2 if intr.name in ('lerp', 'smoothstep') else 0
    param_names_no_self = [
        param.name for idx, param in enumerate(intr.params[1:])
            if idx != self_idx
    ]
    param_str = ', '.join(['self'] + param_names_no_self)
    impl_file.write(f'\tdef {intr.name}({param_str}):\n')

    init_arg_names = param_names_no_self.copy()
    init_arg_names.insert(self_idx, 'self')

    init_arg_str = ', '.join([f'{{{name}}}' for name in init_arg_names])
    impl_file.write(
        f'\t\treturn self.__class__( f\'{intr.name}({init_arg_str})\' )\n\n'
    )

    def _generate_test_func(dtype_suffix : str):
        func_name = f'test_{intr.name}_Float{dtype_suffix}'
        dtype_name = f'sh.Float{dtype_suffix}'
        test_file.write(
            f'\twith sh.function("{func_name}", {dtype_name})('
        )
        test_file.write(', '.join([
            f'{arg_name} = {dtype_name}' for arg_name in param_names_no_self
        ]))
        test_file.write('):\n')
        test_file.write(
            f'\t\tsh.return_( sh.g_f{dtype_suffix}.{intr.name}('
        )
        test_file.write(', '.join([
            f'{arg_name} = sh.{arg_name}' for arg_name in param_names_no_self
        ]))
        test_file.write(') )\n\n')

    _generate_test_func('')

    for dim in range(1, 5):
        _generate_test_func(str(dim))

    for row in range(1, 5):
        for col in range(1, 5):
            _generate_test_func(f'{row}x{col}')


def _generate_intrinsics(
    float_impl_file, float_test_file,
    numeric_impl_file, numeric_test_file
):
    for f in (
        float_impl_file, float_test_file,
        numeric_impl_file, numeric_test_file
    ):
        f.write(impl_header)

    for f in (float_impl_file, numeric_impl_file):
        f.write('class AnyLayoutMixin:\n')

    for f in (float_test_file, numeric_test_file):
        f.write('def test(sh):\n')

    db = hct.get_db_hlsl()

    for intr in sorted(db.intrinsics, key = lambda intr: intr.name):
        if (   intr.ns != "Intrinsics"
            or intr.vulkanSpecific
            or intr.hidden
            or any(p.template_list != 'LITEMPLATE_ANY' for p in intr.params)
        ):
            continue

        # This param represents the return value, check the assumption that
        # it's always the first one
        assert(intr.params[0].name == intr.name)

        if all( param.component_list in (
                'LICOMPTYPE_FLOAT_LIKE',
                'LICOMPTYPE_ANY_FLOAT',
                'LICOMPTYPE_FLOAT_DOUBLE'
            ) for param in intr.params
        ):
            _generate_intrinsic(intr, float_impl_file, float_test_file)
        elif all(
            param.component_list == 'LICOMPTYPE_NUMERIC' for param in intr.params
        ):
            _generate_intrinsic(intr, numeric_impl_file, numeric_test_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description =   "Generate Metashade code for HLSL intrinsics"
                        "from their definitions in DXC"
    )
    parser.add_argument(
        "--metashade-root",
        help = "Path to the root directory of the Metashade repo"
    )
    args = parser.parse_args()
    
    if not os.path.isdir(args.metashade_root):
        raise NotADirectoryError(args.metashade_root)

    impl_dir_path = os.path.join(
        args.metashade_root, 'metashade', 'hlsl', 'sm6'
    )
    test_dir_path = os.path.join(args.metashade_root, 'tests')

    def _get_file_path(dir_path, dtype_category : str):
        return os.path.join(
            dir_path,
            f'_auto_{dtype_category}_intrinsics.py'
        )

    with (open(_get_file_path(impl_dir_path, 'float'), 'w')
            as float_impl_file,
          open(_get_file_path(test_dir_path, 'float'), 'w')
            as float_test_file,
          open(_get_file_path(impl_dir_path, 'numeric'), 'w')
            as numeric_impl_file,
          open(_get_file_path(test_dir_path, 'numeric'), 'w')
            as numeric_test_file
    ):
        _generate_intrinsics(
            float_impl_file, float_test_file,
            numeric_impl_file, numeric_test_file
        )


"""
A module that define a %%rs magic to compile rust as binary or web-assembly in jupyter
"""

# inspired by https://github.com/Carreau/cffi_magic/blob/master/cffi_magic/__init__.py

from cffi import FFI
from hashlib import md5
import subprocess
import io
import os
import re
from sys import platform
import shlex
import argparse
import pixiedust_node

from IPython.core.magic import (Magics, magics_class, cell_magic)

hash_code = lambda s:md5(s.encode()).hexdigest()

def xstr(s):
    return '' if s is None else str(s)

lib_pre = 'lib'

if platform == 'darwin':
    ext = 'dylib'
elif platform == 'win32':
    lib_pre = ''
    ext = 'dll'
else:
    ext = 'so'

cargo_toml="""
[package]
name = "{name}"
version = "0.0.1"
authors = ["No-one InParticular <nobody@example.com>"]
[lib]
name = "{name}"
crate-type = ["{crateType}"]
"""

@magics_class
class RS(Magics):

    @cell_magic
    def rs(self, line, cell):
        """
        %%rs builds and links rust code
        USAGE:
            %%rs [OPTIONS] func_prototype
            <rust-code>

        OPTIONS:
            -n, --new              cleans .rs folder and deletes Cargo.toml
            -l, --lib "lib-name"   calls cargo-add with libname
                rand
                "local_experiment --path=lib/trial-and-error/"
                "lib/trial-and-error/"
            -w, --wasm "var-name"  build wasm-bindgen web-assembly
                                   to be loaded in node

        EXAMPLE:
            creates sources in .rs/... compiles, links with cffi
            and adds rand_it to the namespace

            %%rs --new -l rand int rand_it(int);
            extern crate rand;
            use rand::Rng;
            #[no_mangle]
            pub extern fn rand_it(x: i32) -> i32 {
                let mut rng = rand::thread_rng();
                x*3 + rng.gen::<i32>()
            }
        """

        hashname = '_rs_%s' % hash_code(line+cell)

        parser = argparse.ArgumentParser()
        parser.add_argument('-n', '--new', action='store_true')
        parser.add_argument('-l', '--lib', action='append')
        parser.add_argument('-w', '--wasm', nargs='?', default=None, const="wasm")
        parser.add_argument('func_prototype', nargs='*')
        args = parser.parse_args(shlex.split(line))

        # pure wasm32-unknown-unknown without wasm_bindgen is not supported
        # due to various __rust_start_panic unreachable
        #
        args.wasm_bindgen = args.wasm
        isWasmBindgen = args.wasm_bindgen is not None
        isWasm = args.wasm is not None or isWasmBindgen


        # prepare directory
        #
        cwd = '.rs'
        try:
            os.makedirs(cwd +'/src')
        except OSError:
            pass

        # clean directory
        #
        if args.new:
            subprocess.run(["cargo", "clean"], cwd=cwd)
            try:
                os.remove(cwd +'/Cargo.toml')
            except OSError:
                pass

        # create cargo.toml
        #
        with io.open(cwd +'/Cargo.toml','wb') as f:
            t = cargo_toml.format(
                name=hashname,
                crateType='cdylib' if isWasm else 'dylib')
            f.write(t.encode('utf-8'))

        # collect libraries see cargo-edit
        #
        libs = ['wasm-bindgen' if isWasmBindgen else 'libc'] + (args.lib or [])
        for lib in libs:
            subprocess.run(["cargo", "add"] + shlex.split(lib), cwd=cwd)

        # create source file
        #
        with io.open(cwd +'/src/lib.rs', 'wb') as f:
            f.write(cell.encode())

        # build
        #
        cmd = ['cargo', 'build'] \
            + (['--target', 'wasm32-unknown-unknown'] if isWasm else []) \
            + (['--release'] if not isWasmBindgen else [])
        subprocess.run(cmd, cwd=cwd)

        # build wasm-bindgen and load using pixie-node
        #
        if isWasmBindgen:
            subprocess.run(["wasm-bindgen",
                            "--out-dir", "./target",
                            "--nodejs",
                            "--no-typescript",
                            "./target/wasm32-unknown-unknown/debug/" + hashname + ".wasm"], cwd=cwd)

            ip = get_ipython()
            cell = "{var} = require('{cwd}/target/{name}.js')".format(
                var=args.wasm_bindgen,
                cwd=os.getcwd()+'/'+cwd,
                name=hashname)
            ip.run_cell_magic('node', None, cell)

        # bind library with cffi
        #
        else:
            func = ' '.join(args.func_prototype).strip()
            ffi = FFI()
            ffi.cdef(func)
            lib = "{cwd}/target/release/{pre}{name}.{ext}".format(
                cwd=cwd,
                name=hashname,
                pre=lib_pre,
                ext=ext)
            mod = ffi.dlopen(lib)

            exports =  re.findall('([a-zA-Z0-9_]+)\(', func)
            for attr in exports:
                self.shell.user_ns[attr] = getattr(mod, attr)
                print("injecting `%s` in user ns" % (attr,))


ip = get_ipython()
ip.register_magics(RS)
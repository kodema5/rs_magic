# jupyter %%rs magic

%%rs?

```
%%rs builds and links rust code as binary or web-assembly

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
```

see [Dockerfile](https://docs.docker.com/engine/reference/builder/) for dependencies..

  * [rust](https://www.rust-lang.org/) and [cargo](https://github.com/rust-lang/cargo) nightly for wasm-bindgen
  * [cargo-edit](https://github.com/killercup/cargo-edit) to download and include rust libraries
  * [cffi](https://dbader.org/blog/python-cffi) to load rust binary as c library
  * [wasm-bindgen-cli](https://rustwasm.github.io/wasm-bindgen/whirlwind-tour/basic-usage.html) to compile binary to wasm
  * [pixiedust_node](https://github.com/pixiedust/pixiedust_node) to load wasm via %%node

see test.ipynb for usage

  * docker build -t jupyter-rs-magic .
  * docker run --rm --name jupyter-rs-magic -p 8888:8888 -v ${pwd}:/home/jovyan/work jupyter-rs-magic
  * access http://localhost:8888/notebooks/work/test.ipynb (password:rei)
  * docker stop jupyter-rs-magic


# docker build -t jupyter-rs-magic .

FROM jupyter/datascience-notebook

# install rust nightly for wasm_bindgen
#
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y \
    && /$HOME/.cargo/bin/rustup install nightly \
    && /$HOME/.cargo/bin/rustup target add wasm32-unknown-unknown --toolchain nightly \
    && /$HOME/.cargo/bin/rustup component add llvm-tools-preview --toolchain nightly \
    && /$HOME/.cargo/bin/rustup default nightly

ENV PATH /$HOME/.cargo/bin:$PATH

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        pkg-config \
        libssl-dev

RUN echo "application/wasm       wasm" >> /etc/mime.types

USER jovyan

RUN cargo install \
    cargo-edit \
    wasm-bindgen-cli

COPY setup.py /rs_magic/
COPY readme.md /rs_magic/
COPY rs_magic/__init__.py /rs_magic/rs_magic
RUN pip install --upgrade pip \
    && pip install /rs_magic

# pwd=rei
#
CMD ["start-notebook.sh", "--NotebookApp.password='sha1:bc9ab372753f:6a8cd6b1a0cb9052cd66da00f5690ae3ae4f3b25'"]
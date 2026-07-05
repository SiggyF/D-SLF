FROM quay.io/pypa/manylinux2014_x86_64

ENV CC=gcc CXX=g++

WORKDIR /repo
COPY . /repo

RUN mkdir -p build && cd build && \
    cmake -DUSE_FAST_MATH=OFF -DUSE_FAST_TANH=ON -DCMAKE_INSTALL_PREFIX=../dist -DCMAKE_BUILD_TYPE=Release .. && \
    make -j4 install

RUN /opt/python/cp311-cp311/bin/python -m pip install --upgrade pip setuptools wheel cffi

RUN cd wrappers/python && \
    /opt/python/cp311-cp311/bin/python setup.py build_ext --library-dirs=../../dist/lib --include-dirs=../../include bdist_wheel --py-limited-api=cp311 && \
    /opt/python/cp311-cp311/bin/python -m pip install dist/*.whl

ENV LD_LIBRARY_PATH=/repo/dist/lib

CMD ["/opt/python/cp311-cp311/bin/python", "examples/python/steady.py"]

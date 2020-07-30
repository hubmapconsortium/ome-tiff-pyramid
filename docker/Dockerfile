ARG BUILD_IMAGE=gradle:6.2.1-jdk8

#
# Build phase: Use the gradle image for building.
#
FROM ${BUILD_IMAGE} as build

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qq \
 && apt-get -y install \
    libblosc1 \
    tzdata \
    zeroc-ice-all-runtime \
    zip \
 && rm -rf /var/cache/apt/*

WORKDIR /bioformats_pyramid

ENV BIOFORMATS2RAW_VERSION=v0.2.4
# Clone tiff-to-raw pyramid code.
RUN git clone -b ${BIOFORMATS2RAW_VERSION} https://github.com/glencoesoftware/bioformats2raw.git \
 && cd bioformats2raw \
 && gradle build \
 && cd build/distributions \
 && rm bioformats2raw*tar \
 && unzip bioformats2raw*zip \
 && rm -f bioformats2raw*zip \
 && cd ../.. \
 && mv build/distributions/bioformats2raw* /opt/bioformats2raw

ENV RAW2OMETIFF_VERSION=v0.2.7
# Clone raw pyramid to tiff repo.
RUN git clone -b ${RAW2OMETIFF_VERSION} https://github.com/glencoesoftware/raw2ometiff.git \
 && cd raw2ometiff \
 && gradle build \
 && cd build/distributions \
 && rm raw2ometiff*tar \
 && unzip raw2ometiff*zip \
 && rm -f raw2ometiff*zip \
 && cd ../.. \
 && mv build/distributions/raw2ometiff* /opt/raw2ometiff

# Set working directory containing new cli tools.
WORKDIR /opt
COPY bin /opt

CMD ["/bin/bash"]

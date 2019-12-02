# Phase One - `Setup`
First, install the necessary dependencies:

```sudo apt -y install \
  autoconf-archive \
  libcmocka0 \
  libcmocka-dev \
  build-essential \
  git \
  pkg-config \
  gcc \
  g++ \
  m4 \
  libtool \
  automake \
  autoconf \
  libdbus-glib-1-dev \
  libssl-dev \
  glib2.0 \
  cmake \
  libssl-dev \
  libcurl4-gnutls-dev \
  doxygen \
  efitools'''
  
Download the TPM2 dependency files to a comomn directory
```git clone https://github.com/tpm2-software/tpm2-tss.git
  git clone https://github.com/tpm2-software/tpm2-abrmd.git
  git clone https://github.com/tpm2-software/tpm2-tools.git```

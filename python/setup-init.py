#!python3

import subprocess
import os
from os import path
from shutil import copyfile
import configparser
from subprocess import CalledProcessError

def dependencies():
    deps = configparser.ConfigParser()
    deps.read("python/dependencies.ini")
    print(deps.sections())
    pkg = deps.get('DEPENDS', 'APT')
    pkg = pkg.split()

    for package in pkg:
        failed = ""
        try:
            subprocess.run("apt install " + package, capture_output=True,check=True)
        except CalledProcessError:
            failed = failed + deps[package] + " "
    subprocess.run("apt-get install " + deps.get("DEPENDENCIES", "APT_GET"), capture_output=True, check=True)
    print("The following packages failed to install: " + failed.strip() + "." )

def shell(command):
    subprocess.run(command, capture_output=True)

shell("cd /usr/local/src; git clone https://github.com/tpm2-software/tpm2-tss.git")
shell("cd /usr/local/src/tpm2-tss; ./bootstrap; ./configure --with-udevrulesdir=/etc/udev/rules.d")
shell("cd /usr/local/src/tpm2-tss; make; make install")
dependencies()

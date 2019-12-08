# tpm2KeyUnlock
Adds an automated unlock function based on TPM policy installation

Main Source: https://threat.tevora.com/secure-boot-tpm-2/

# Detailed walkthrough
The setup of TPM unlocking involves three phases. The first phase installs the TPM tools. The second sets up a TPM-signed kernel, recovery kernel, and TPM key. The final step verifies the TPM key is working and finishes setting up the TPM kernel.

# General requirements
- A secure-boot enabled system with a custom key authentication setting in BIOS.
- EFI System Partition (ESP) access for installing custom kernels.
- General understanding of bash commands.
- Patience. Quite a bit of it.

# Current issues
- [IN PROGRESS] The scripts `setup` and `setup2` are designed for my convenience, but can be used on any linux system. A few commands are missing from them that I need to add in. For now, I recommend using only the `Manual Install` directions. I recorded the steps as I recreated them, and so far they work fine for me. If any issues come about, I'll help out as best I can.

- [FIXED] The `passphrase-from-tpm` currently does not allow fallback password entry. I could not figure it out and I currently don't have time since school break ended.

- [NEW] Third-party kernel modules (i.e. NVIDIA drivers) currently do not work with custom boot signatures. There appears to be no current solution. Signing the modules and adding them in through MOKManager appears to only work for the original kernel. Booting from the original kernel allows the kernel modules to load, but booting into the custom modules does not work nicely.

- [NEW] The issue above causes another security issue in which signing tpm2_unseal with the generic kernel causes an exploit. Through the first method, the kernel can be replaced with another generic kernel and makes it possible to retrieve the signature straight from initramfs. The secret can then be read and run through the signed generic kernel. The second method involves using the current kernel to reach `initramfs` and running `cat /usr/local/bin/passphrase-from-tpm`, revealing the hex signature of the tpm's unlock key. The last method involves brute forcing through all available hex values with the generic kernel until tpm unlocks the system with the kernel's signature. 
    - Solution: I am currently looking into this, but without much time right now, it could take a couple weeks to figure out. However, using the custom signed bootloader solves each issue through the following methods: hiding the kernel's signature inside the encrypted drive; allowing only passphrase input; after 60 seconds, the system times out and panics, causing a reboot; even though the attacker may figure out the hex value, the only way to use it to unlock the custom bootloader is through reaching `initramfs` and loading the hex value through there - the system reboots before that can happen.

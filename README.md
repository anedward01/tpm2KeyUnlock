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

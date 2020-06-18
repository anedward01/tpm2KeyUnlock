# tpm2KeyUnlock
Adds an automated unlock function based on TPM policy configuration

Main Source: https://threat.tevora.com/secure-boot-tpm-2/

# Detailed walkthrough
The setup of TPM unlocking involves three phases. The first phase installs the TPM tools. The second sets up a TPM-signed kernel, recovery kernel, and TPM key. The final step verifies the TPM key is working and finishes setting up the TPM kernel.

# General requirements
- A secure-boot enabled system with a custom key authentication setting in BIOS.
- EFI System Partition (ESP) access for installing custom kernels.
- General understanding of bash commands.
- ~~Patience. Quite a bit of it~~ Not so much patience required anymore, just time.

- Alternatively, non secure boot systems can find support now, but it's still a bit hazy.
- A bootloader to boot the kernel or custom boot options in BIOS.
- Using alternative PCR values (0,2,3,7,8). These should work, but there aren't many sources supporting this.

# TODO
- [FIXED] The scripts `setup` and `setup2` are properly set up to be almost completely automated. `setup` now adds a GRUB entry and sets it to default boot. If GRUB isn't installed, it continues installation. Adding the kernel to a bootloader is recommended, but the EFI stub can be directly added to BIOS. `setup2` now automatically finds the first LUKS drive using grep and lots of regex. It pulls the partition name and UUID to modify /etc/crypttab and add `secret.bin` to `cryptsetup`. Finally, the scripts now support SHA 256 PCR banks. If the banks are unavailable or unpopulated, the script defaults to SHA 1. 

- [FIXED] The `passphrase-from-tpm` now allows fallback passphrase entry. This is pretty solid and consistent now.

- [FIXED] Third-party kernel modules (i.e. NVIDIA drivers) SHOULD be supported using a new `bootChain-update` script. The previous one had the kernel version and release candidate hardcoded in. This caused issues since some modules result in new kernel versions when installed. The script now uses the `/boot/vmlinuz` and `/boot/initrd.img` symlinks to get the proper kernel.

- [NEW] [FIXED] I have begun testing with a larger variety of hardware. So far, Intel's fTPM (PTT) seems to be properly supported. There is an issue with non secure boot systems. Since PCR 7 isn't required to run a security check, it appears that an unsigned kernel can be used to boot into the system using TPM. However, on the hardware I have tested on, TPM PCR 8 runs an independent security check which differs between unsigned kernels and signed kernels. As long as a kernel is signed, PCR 8 can be appended to line 58 and 59 of `setup2`. I will look into a system check for secure boot. I believe `mokutil` should provide the answer as soon as I get around to it.

- [NEW] Trying to use this script on a system with multiple LUKS partitions may select the incorrect LUKS partition. I'll provide a solution for this at a later date.
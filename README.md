# tpm2KeyUnlock
Adds automatic decryption function based on TPM policy configuration

Main Source: https://threat.tevora.com/secure-boot-tpm-2/

# Using the scripts
`setup` automatically pulls out the LUKS and EFI boot partition using blkid and grep. The only input it requires is a `cryptsetup` password and a simple `yes`. The script supports flags as follows:

  * -b: Manually sets the boot partition by UUID
  * -l: Manually sets the LUKS partition by UUID
  * -p: Provides the `cryptsetup` password for automation
  * -r: Manually sets the root partition under /dev/mapper/
  * -y Gives the script a clear go-ahead for signed kernel creation

Once it finishes the first round, it will try to set up a GRUB menu entry. If the system does not use GRUB, it will continue running after giving a notice. Next, a `systemd` file will be added and enabled to run at boot. The `tpm2keyunlock.service` file will be installed under /etc/systemd/system and run TPM commands to persist secret in memory. The service will then disable itself after finishing setting up `/etc/crypttab` and `/usr/local/bin/passphrase-from-tpm` with the appropriate PCR hash method and persistent handle.

# Detailed walkthrough
The setup of TPM unlocking involves three phases. The first phase installs the TPM tools. The second sets up a TPM-signed kernel and TPM key. The final step verifies the TPM key is working and finishes setting up the TPM kernel.

# General requirements
- A secure-boot enabled system with a custom key authentication setting in BIOS.
- EFI System Partition (ESP) access for installing custom kernels.
- General understanding of bash commands.
- ~~Patience. Quite a bit of it~~ Not so much patience required anymore, just time.

# Using cloud-init to automate deployment and installation
I created an overview over at https://www.edwardssite.com/cloud-init outlining the details of how to automate the deployment and installation process of this project using cloud-init and Ubuntu's autoinstall settings. Pretty much everything needed is explained there, and reference files are included.

# Post quarantine update
Earlier in the year I received a request to continue developing the project. A lot of progress towards security and automation has been made. The project and its development has been allowed to keep its open source license, so I will leave the project up! As far as development goes, here are the major points:

- Symbolic linking and regular expressions allow the script to pull up LUKS and boot partitions without interference. A signed TPM kernel is compiled using the latest kernel. Editing to /etc/crypttab and passphrase-from-tpm are also included.
- SHA 256 is now supported. The script will check for SHA 256 PCR 0. If it doesn't exist or it's value is empty, it will default back to SHA 1. TPM spec 1.x and SHA 256 banks must be enabled to ensure compatibility.
- A GRUB menu entry is now thrown in. In case you don't use GRUB, it won't force you to have it. It will also set the signed TPM kernel as the default boot option on startup.
- Initramfs in the signed kernel now requires the root device. This wasn't an issue before, but a fix was found.
- A systemd service file to pick up after reboot. As soon as the TPM signed kernel is unlocked, in about three minutes the TPM will have the secret key secured and the service will disable itself. Double-checking journalctl is recommended, of course.
- Boot parameters are now included. If there are multiple LUKS drives, specify `-l [UUID]` to set the luks drive. A cryptsetup password is needed to add the secret into LUKS, so `-p [pass]` along with `-y` allows for automated configurations. Only the first setup script takes and needs parameters.
- The default PCR banks have been set to 0, 2, 3, 7, 8. This supports both secure boot and non-secure boot devices. Testing has been run on a secure boot laptop and a non-secure boot device and both have worked consistently. Of course, not all devices are the same, so if there are any problems please open an issue.

There is a lot more coming soon. There is definitely a lot of improvement that can be made, and I am looking forward to it. I am glad you read this far, and thank you for your time!

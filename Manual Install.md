# Requirements
- A non-encrypted partition to store Secure Boot keys in (flash drive, EFI partition).
- Patience
- Using a root bash is recommended, else add `sudo` at the beginning of each command.
- Creating a backup kernel is recommended, but can mitigate security. However, without the backup kernel, if the TPM security changes, the system will be completely locked out if the TPM kernel is not properly updated.

# Phase One - `Setup`
First, install the necessary dependencies:

    apt -y install \
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
    libgcrypt20-dev \
    libjson-c-dev \
    autoconf \
    libdbus-glib-1-dev \
    libssl-dev \
    glib2.0 \
    cmake \
    libssl-dev \
    libcurl4-gnutls-dev \
    doxygen \
    uuid-dev \
    efitools


Download the TPM2 dependency files to a comomn directory

    git clone https://github.com/tpm2-software/tpm2-tss.git
    git clone https://github.com/tpm2-software/tpm2-abrmd.git
    git clone https://github.com/tpm2-software/tpm2-tools.git

Set up tpm2-tss from source. Since the daemon `abrmd` needs direct access to the computer hardware, `./configure` is appended with root privileges.
    
    ./bootstrap
    ./configure --with-udevrulesdir=/etc/udev/rules.d
    make
    make install
    
Create a new user group labeled `tss` that the daemon will attach to later.
    
    sudo useradd --system --user-group tss
    
Set up tpm2-abrmd from source. The daemon service needs direct access to the system, so the daemon is appended to allow access to the TPM
 
    ./bootstrap
    ./configure --with-dbuspolicydir=/etc/dbus-1/system.d --with-systemdsystemunitdir=/lib/systemd/system
    make
    make install
    
Reload the services, enable the new TPM daemon, and launch it.

    udevadm control --reload-rules && sudo udevadm trigger
    pkill -HUP dbus-daemon
    systemctl daemon-reload
    ldconfig
    systemctl enable tpm2-abrmd
    service tpm2-abrmd start

Set up tpm-tools from source. Bootstrap it a few times before installing to avoid install issues.
    
    ./bootstrap
    ./bootstrap
    ./bootstrap
    ./configure
    make
    make install
    
Create new signature keys for our signed TPM kernel. This step prevents the original kernel from unlocking the system, mitigating security issues. The signed kernel creates keys to allow secure boot.

NOTE: These keys will need to be kept somewhere safe. They are needed to resign the kernel after updates. If they are lost, the backup kernel will need to be used to resign the TPM kernel. For extra security, new keys can be generated at any time, but must be added to the secure boot entry.
FOR SECURE BOOT: Transfer the `.auth` files to the unencrypted partition. Go into BIOS under Secure Boot, then enable some form of `Custom keys` or `Custom` mode. Only the `db.auth` file needs to be added to the `db` database, but the other keys can be added. 

    #Create Platform Key
    uuidgen --random > GUID.txt
    openssl req -newkey rsa:2048 -nodes -keyout PK.key -new -x509 -sha256 -days 3650 -subj "/CN=my Platform Key/" -out PK.crt
    openssl x509 -outform DER -in PK.crt -out PK.cer
    cert-to-efi-sig-list -g "$(< GUID.txt)" PK.crt PK.esl
    sign-efi-sig-list -g "$(< GUID.txt)" -k PK.key -c PK.crt PK PK.esl PK.auth

    #Create Key Exchange Key
    openssl req -newkey rsa:2048 -nodes -keyout KEK.key -new -x509 -sha256 -days 3650 -subj "/CN=my Key Exchange Key/" -out KEK.crt
    openssl x509 -outform DER -in KEK.crt -out KEK.cer
    cert-to-efi-sig-list -g "$(< GUID.txt)" KEK.crt KEK.esl
    sign-efi-sig-list -g "$(< GUID.txt)" -k PK.key -c PK.crt KEK KEK.esl KEK.auth

    #Creating Signature Database Key
    openssl req -newkey rsa:2048 -nodes -keyout db.key -new -x509 -sha256 -days 3650 -subj "/CN=my Signature Database key/" -out db.crt
    openssl x509 -outform DER -in db.crt -out db.cer
    cert-to-efi-sig-list -g "$(< GUID.txt)" db.crt db.esl
    sign-efi-sig-list -g "$(< GUID.txt)" -k KEK.key -c KEK.crt db db.esl db.auth
    
Set up `cmdline.txt` and enter custom commands for the kernel. For now, leaving the commands blank is recommended.

    touch cmdline.txt
    
Wrapping up phase 1, create the new TPM kernel and the backup kernel.

    objcopy \
	--add-section .osrel=/etc/os-release --change-section-vma .osrel=0x20000 \
	--add-section .cmdline=cmdline.txt --change-section-vma .cmdline=0x30000 \
	--add-section .linux="/boot/vmlinuz-5.0.0-36-generic" --change-section-vma .linux=0x40000 \
	--add-section .initrd="/boot/initrd.img-5.0.0-36-generic" --change-section-vma .initrd=0x3000000 \
	/usr/lib/systemd/boot/efi/linuxx64.efi.stub /boot/efi/EFI/BOOT/BOOTX64.EFI
    sbsign --key db.key --cert db.crt --output /boot/efi/EFI/BOOT/BOOTX64.EFI /boot/efi/EFI/BOOT/BOOTX64.EFI

    objcopy \
	--add-section .osrel=/etc/os-release --change-section-vma .osrel=0x20000 \
	--add-section .cmdline=cmdline.txt --change-section-vma .cmdline=0x30000 \
	--add-section .linux="/boot/vmlinuz-5.0.0-36-generic" --change-section-vma .linux=0x40000 \
	--add-section .initrd="/boot/initrd.img-5.0.0-36-generic" --change-section-vma .initrd=0x3000000 \
	/usr/lib/systemd/boot/efi/linuxx64.efi.stub /boot/efi/EFI/BOOT/BOOT_RECX64.EFI
    sbsign --key db.key --cert db.crt --output /boot/efi/EFI/BOOT/BOOT_RECX64.EFI /boot/efi/EFI/BOOT/BOOT_RECX64.EFI
    
Reboot the computer into the TPM kernel.

# Phase 2 - `setup2`

Download the `tpm2Hook` file. Make sure that it is executable. label it `tpm2` while copying it into `/etc/initramfs-tools/hooks` and `/usr/share/initramfs-tools/hooks`. Make sure the copied file is executable. Set permissions to allow owner to modify the file and all else to read and execute.

    chmod +x tpm2Hook
    chmod 755 tpm2Hook
    cp tpm2Hook /etc/initramfs-tools/hooks/tpm2
    chmod +x /etc/initramfs-tools/hooks/tpm2
    chmod 755 /etc/initramfs-tools/hooks/tpm2
    cp tpm2Hook /usr/share/initramfs-tools/hooks/tpm2
    chmod +x /usr/share/initramfs-tools/hooks/tpm2
    chmod 755 /usr/share/initramfs-tools/hooks/tpm2
    
Create a new folder to store TPM-related files in. Create a new secret key used to unlock the encrypted drive. Store it in /root/ for boot access and allow only root access for protection. Add the key to LUKS Set up the new TPM environment. 

NOTE: They key is important. It is the key to unlock the system. Keep it safe, and use any desired method to secure it.
The only requirement is it needs to be accessible during boot and kernel creation.

    dd if=/dev/urandom of=secret.bin bs=32 count=1
    chmod 0400 secret.bin
    cp secret.bin /root/secret.bin
    chmod 0400 /root/secret.bin
    cryptsetup luksAddKey [INSERT DRIVE DIRECTORY] /root/secret.bin
    
Clear the TPM state to allow read/write. If you know what you are doing, skip `tpm2_clear` and continue to the next steps.
If you really know what you are doing, the values `0,2,3,7` can be changed. Be aware that improperly handling the TPM entries
can cause issues and lock out the tpm, requiring a tpm clear state.

    tpm2_clear
    tpm2_pcrread sha1:0,2,3,7 -o pcrs.bin
    tpm2_createpolicy --policy-pcr -l sha1:0,2,3,7 -f pcrs.bin --policy policy.digest
    tpm2_createprimary -c primary.context
    tpm2_create -u obj.pub -r obj.priv -C primary.context -L policy.digest --attributes "noda|adminwithpolicy|fixedparent|fixedtpm" -i secret.bin
    tpm2_load -C primary.context -u obj.pub -r obj.priv -c load.context
    tpm2_evictcontrol -c load.context
    
The last command should give a hex value. For example, `0,2,3,7` tends to spit out `0x81000000`. Record this value.
Download the `passphrase-from-tpm` file and change the default value listed above to the recorded hex value. If you modified the PCR values, change the tpm2_unseal line `pcr:sha1:[0,2,3,7]` to the new values. Save the file to /usr/local/bin. Make sure the file is executable. Change permissions to allow author full control else read/write

    cp passphrase-from-tpm /usr/share/bin/passphrase-from-tpm
    chmod +x /usr/share/bin/passphrase-from-tpm
    chmod 755 /usr/share/bin/passphrase-from-tpm

Edit `/etc/crypttab`. It should have a table in the format 
`drive_name UUID/drive_path keys commands`
Mine, for example, is:
`sda3_crypt UUID=xxxxxxxxxxxx none luks,discard`

Edit keys and change `none` to `/root/secret.bin` or append with a comma delimiter between keys.
Edit commands and append with `keyscript=/usr/local/bin/passphrase-from-tpm`.
The finished product should look as follows
`sda3_crypt UUID=xxxxxxxxxxxx /root/secret.bin luks,discard,keyscript=/usr/local/bin/passphrase-from-tpm`

Finally, BEFORE RECOMPILING THE KERNEL, restart the system into the TPM kernel

# Phase 3

This is the shortest step. 

Make sure you can read the secret key by running line 6 from `passphrase-from-tpm`. Modify the hex value and pcr values as needed.

    /usr/local/bin/tpm2_unseal -c 0x81000000 --auth pcr:sha1:0,2,3,7
    
If it throws an error, something went wrong. go back to phase 2 and walk through the steps, making sure to double-check or copy everything as necessary. Otherwise, continue to the next step.

Recall the command to create a custom signed kernel:

    objcopy \
	--add-section .osrel=/etc/os-release --change-section-vma .osrel=0x20000 \
	--add-section .cmdline=cmdline.txt --change-section-vma .cmdline=0x30000 \
	--add-section .linux="/boot/vmlinuz-5.0.0-36-generic" --change-section-vma .linux=0x40000 \
	--add-section .initrd="/boot/initrd.img-5.0.0-36-generic" --change-section-vma .initrd=0x3000000 \
	/usr/lib/systemd/boot/efi/linuxx64.efi.stub /boot/efi/EFI/BOOT/BOOTX64.EFI
    sbsign --key db.key --cert db.crt --output /boot/efi/EFI/BOOT/BOOTX64.EFI /boot/efi/EFI/BOOT/BOOTX64.EFI

Create a new script or download `bootChain-Update` and add a path to the directory with the signatures created earlier. Edit `cmdline.txt` and add `panic=60`; this prevents the dropdown shell from appearing after TPM unlock fails. This is necessary to prevent access to the secret from the shell.
Launch the script. It will create a new signed kernel. If all goes well, you can reboot. When you do, it should automatically unlock LUKS for you and you're all done! If it doesn't, record the error, boot into the backup kernel, and work back through the guide.

Although unrecommended, you can delete the backup boot kernel and have the system rely solely on TPM security.
    

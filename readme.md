# MultiAxisController_go8010


- serial share with wsl (windows)
```sh
usbipd list
usbipd.exe bind --busid 2-1
usbipd.exe attach --wsl --busid 2-1

usbipd detach --busid 2-1
usbipd unbind --busid 2-1
```
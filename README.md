A simple ukhas.net node in Python for the Raspberry Pi.

## Hardware

You need a Raspberry Pi with an RFM69 radio module connected, for
example with my [RFM69
hat](https://github.com/russss/raspberry-pi-rfm69).

## Usage

* Append `dtparam=spi=on` to `/boot/config.txt` to enable SPI
* If you want to use 1-wire sensors, add `dtoverlay=w1-gpio` to `/boot/config.txt`
* Reboot so these options take effect.
* `sudo apt-get install python-dev python-pip`
* `sudo pip install rfm69`
* Copy `etc/ukhasnet.example.cfg` to `/etc/ukhasnet.cfg` and edit to configure

You should then be able to run the node with `sudo python ./node.py` (it
must run as root to access SPI and GPIO).

## To run at boot using systemd

* Copy `etc/ukhasnet-node.service` into `/etc/systemd/system/`. Make sure
  the path to this code is correct in that file.
* Run `systemctl daemon-reload` to reload the systemd config.
* Run `systemctl enable ukhasnet-node` to enable, and `systemctl
  start ukhasnet-node` to start.
* Logs will be visible in `/var/log/syslog`

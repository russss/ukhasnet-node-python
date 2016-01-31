import ConfigParser
from rfm69 import RFM69
from ukhas_config import config as rfm_config
from time import time, sleep
import requests
from requests.exceptions import ConnectionError
import logging

logging.basicConfig(level=logging.INFO)


class UKHASNetNode(object):

    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.config = ConfigParser.ConfigParser()
        self.config.read('/etc/ukhasnet.cfg')
        self.node_name = self.config.get('main', 'name')
        if self.config.get('main', 'latitude') and self.config.get('main', 'longitude'):
            self.location = "%s,%s" % (self.config.get('main', 'latitude'),
                                       self.config.get('main', 'longitude'))
        else:
            self.location = None
        self.counter = 'a'
        self.http = requests.Session()
        self.rfm69 = RFM69(reset_pin=21,
                      dio0_pin=20,
                      spi_channel=0,
                      config=rfm_config)

    def get_packet_counter(self):
        current = self.counter
        if ord(self.counter) == 122:
            self.counter = 'b'
        else:
            self.counter = chr(ord(self.counter) + 1)
        return current

    def send_our_packet(self):
        if not self.config.getboolean('node', 'transmit'):
            return
        packet = self.generate_packet()
        self.submit_packet(packet)
        self.broadcast_packet(packet)

    def generate_packet(self):
        counter = self.get_packet_counter()
        temp = self.rfm69.read_temperature()
        packet = "3" + counter
        if self.location:
            packet += "L" + self.location
        if temp:
            packet += "T" + str(temp)
        packet += "[%s]" % self.node_name
        return packet

    def submit_packet(self, packet, rssi=None):
        post_data = {'origin': self.node_name, 'data': packet}
        if rssi is not None:
            post_data['rssi'] = int(rssi)

        try:
            resp = self.http.post("http://www.ukhas.net/api/upload", data=post_data)
        except ConnectionError:
            self.log.exception("Error connecting to ukhas.net")
            return False

        if resp.status_code != 200 or resp.json()['error'] != 0:
            self.log.error("Error submitting packet to ukhas.net: %s", resp.content)
            return False
        else:
            return True

    def relay_packet(self, packet, rssi):
        try:
            rpt = int(packet[0]) - 1
            bkt = packet.index('[')
        except ValueError:
            self.log.warn("Got invalid packet: %s")
            return

        if rpt < 0:
            self.log.info("Dropping packet, repeat limit is reached")
            return

        repeaters = packet[bkt + 1:-1].split(',')
        if self.node_name in repeaters:
            self.log.info("Dropping packet, we already relayed")
            return

        repeaters.append(self.node_name)

        new_packet = bytearray(str(rpt) + packet[1:bkt] + '[' + ','.join(repeaters) + ']', 'ascii')

        if self.config.getboolean('node', 'gateway'):
            self.submit_packet(packet, rssi)

        if self.config.getboolean('node', 'repeat'):
            self.broadcast_packet(new_packet)

    def broadcast_packet(self, packet):
        self.log.info("Transmitting packet: %s", packet)
        self.rfm69.send_packet(packet, preamble=0.05)

    def run(self):
        self.rfm69.calibrate_rssi_threshold()
        last_calibration = time()
        self.send_our_packet()
        last_sent = time()
        while True:
            data = self.rfm69.wait_for_packet(timeout=60)
            if data is not None:
                packet, rssi = data
                try:
                    packet = packet.decode('ascii') # packet is a bytearray
                except UnicodeDecodeError:
                    self.log.warn("Received valid non-ASCII packet: %s", packet)
                else:
                    self.log.info("Received packet: %s, rssi: %s", packet, rssi)
                    sleep(0.2)
                    self.relay_packet(packet, rssi)

            if time() - last_sent > 120:
                self.send_our_packet()
                last_sent = time()

            if time() - last_calibration > 3600 or self.rfm69.rx_restarts > 5:
                self.rfm69.calibrate_rssi_threshold()
                last_calibration = time()

n = UKHASNetNode()
n.run()

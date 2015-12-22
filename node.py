from rfm69 import RFM69
from config import config
from time import time, sleep
import requests
import logging

logging.basicConfig(level=logging.DEBUG)


class UKHASNetNode(object):

    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.node_name = "RUSSGW"
        self.location = "51.54,-0.09"
        self.counter = 'a'
        self.http = requests.Session()
        self.rfm69 = RFM69(reset_pin=21,
                      dio0_pin=20,
                      spi_channel=0,
                      config=config)

    def get_packet_counter(self):
        current = self.counter
        if ord(self.counter) == 122:
            self.counter = 'b'
        else:
            self.counter = chr(ord(self.counter) + 1)
        return current

    def send_our_packet(self):
        packet = self.generate_packet()
        self.log.info("Transmitting Packet: %s", packet)
        self.submit_packet(packet)
        self.broadcast_packet(packet)

    def generate_packet(self):
        counter = self.get_packet_counter()
        temp = self.rfm69.read_temperature()
        return "3%sL%sT%s[%s]" % (counter, self.location, temp, self.node_name)

    def submit_packet(self, packet, rssi=None):
        post_data = {'origin': self.node_name, 'data': packet}
        if rssi is not None:
            post_data['rssi'] = int(rssi)
        resp = self.http.post("http://www.ukhas.net/api/upload", data=post_data)

        if resp.status_code != 200 or resp.json()['error'] != 0:
            self.log.error("Error submitting packet to ukhas.net: %s", resp.content)
            return False
        else:
            return True

    def relay_packet(self, packet):
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
        self.broadcast_packet(new_packet)

    def broadcast_packet(self, packet):
        self.log.info("Sending packet: %s", packet)
        self.rfm69.send_packet(packet, preamble=0.05)

    def run(self):
        self.rfm69.calibrate_rssi_threshold()
        self.send_our_packet()
        last_sent = time()
        while True:
            data = self.rfm69.wait_for_packet(timeout=60)
            if data is not None:
                packet, rssi = data
                packet = packet.decode('ascii') # packet is a bytearray
                self.log.info("Received packet: %s, rssi: %s", packet, rssi)
                self.submit_packet(packet, rssi)
                sleep(0.2)
                self.relay_packet(packet)

            if time() - last_sent > 120:
                self.send_our_packet()
                self.last_sent = time()

n = UKHASNetNode()
n.run()

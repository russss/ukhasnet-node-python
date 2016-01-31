from rfm69 import RFM69
from ukhas_config import config
import requests
import logging
import sys

logging.basicConfig(level=logging.DEBUG)


rfm69 = RFM69(reset_pin=21,
              dio0_pin=20,
              spi_channel=0,
              config=config)

print("Sending: %s" % sys.argv[1])
rfm69.send_packet(sys.argv[1], preamble=0.1)

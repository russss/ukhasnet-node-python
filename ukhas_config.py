from rfm69.configuration import RFM69Configuration, IRQFlags1, IRQFlags2, OpMode
from rfm69.constants import RF

config = RFM69Configuration()
config.bitrate_msb = 0x3e
config.bitrate_lsb = 0x80
config.fdev_msb = 0x00
config.fdev_lsb = 0xc5
config.frf_msb = 0xd9
config.frf_mid = 0x60
config.frf_lsb = 0x12
config.afc_ctl = RF.AFCLOWBETA_ON
config.lna = RF.LNA_ZIN_50
config.rx_bw = RF.RXBW_DCCFREQ_010 | RF.RXBW_MANT_16 | RF.RXBW_EXP_2
config.afc_fei = RF.AFCFEI_AFCAUTO_ON | RF.AFCFEI_AFCAUTOCLEAR_ON
config.sync_config = RF.SYNC_ON | RF.SYNC_FIFOFILL_AUTO | RF.SYNC_SIZE_2 | RF.SYNC_TOL_0
config.sync_value_1 = 0x2d
config.sync_value_2 = 0xaa
config.packet_config_1.variable_length = True
config.packet_config_1.crc = True
config.rssi_threshold = 180

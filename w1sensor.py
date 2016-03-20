from __future__ import division, absolute_import, print_function, unicode_literals

class W1TempSensor(object):
    def __init__(self, sensor_id):
        self.sensor_id = sensor_id

    def get_temperature(self):
        with open('/sys/bus/w1/devices/%s/w1_slave' % self.sensor_id, 'r') as sensor:
            data = sensor.readlines()

        if data[0].strip().split(' ')[-1] != 'YES':
            return None

        t_value = data[1].strip().split(' ')[-1]
        return int(t_value.split('=')[-1])/1000

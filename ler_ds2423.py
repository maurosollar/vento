#!/usr/bin/env python3
from machine import Pin
import ds2423
import onewire
from time import sleep

_ONE_WIRE_PIN = 0  # IO pin

ow = onewire.OneWire(Pin(_ONE_WIRE_PIN))

counter = ds2423.DS2423(ow)

for rom in counter.scan():
    counter.begin(bytearray(rom))
    #print("CounterId: {}".format(bytearray(rom)))

while True:
    print("CountA: {}, CountB {}".format(
        counter.get_count("DS2423_COUNTER_A"),
        counter.get_count("DS2423_COUNTER_B"))
        )
    sleep(1)


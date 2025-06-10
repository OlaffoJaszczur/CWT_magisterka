#!/usr/bin/python
# -*- coding:utf-8 -*-

import time
import RPi.GPIO as GPIO
import ADS1263

# Reference voltage
REF = 5.07
channel = 0
DRDY_PIN = 17  # BCM numbering

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(DRDY_PIN, GPIO.IN)

# Initialize ADC
ADC = ADS1263.ADS1263()
if ADC.ADS1263_init_ADC1('ADS1263_4800SPS') == -1:
    print("ADC initialization failed.")
    GPIO.cleanup()
    exit()
print("ADC initialized.")

ADC.ADS1263_SetMode(1)  # Continuous mode
print("Set to continuous mode.")

print(f"Initial DRDY state: {GPIO.input(DRDY_PIN)} (0=ready, 1=waiting)")

samples = []
sample_count = 0

try:
    print("Collecting data... Press Ctrl+C to stop.")
    start_time = time.perf_counter()

    # Wait for first DRDY
    while GPIO.input(DRDY_PIN):
        time.sleep(0.00001)
    print("First DRDY detected.")

    while True:
        while GPIO.input(DRDY_PIN):
            time.sleep(0.00001)  # non-blocking wait

        raw = ADC.ADS1263_GetChannalValue(channel)

        if raw >> 31 == 1:
            voltage = REF * 2 - raw * REF / 0x80000000
        else:
            voltage = raw * REF / 0x7fffffff

        samples.append(voltage)
        sample_count += 1

        if sample_count % 100 == 0:
            print(f"Sample {sample_count}: {voltage:.6f} V")

except KeyboardInterrupt:
    elapsed = time.perf_counter() - start_time
    print(f"\nInterrupted by user after {elapsed:.2f} seconds.")
    print(f"Collected {sample_count} samples. Saving to adc_log.csv...")

    with open('adc_log.csv', 'w') as f:
        for v in samples:
            f.write(f"{v:.6f}\n")

    print("Saved to adc_log.csv")

finally:
    ADC.ADS1263_Exit()
    GPIO.cleanup()

from machine import Pin
import utime

led = Pin(15, Pin.OUT)

while True:
    led.value(1)
    print("Ligado")
    utime.sleep_ms(500)
    
    led.value(0)
    print("Desligado")
    utime.sleep_ms(500)

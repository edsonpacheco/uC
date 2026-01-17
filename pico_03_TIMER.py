from machine import Pin, Timer
import machine

led = Pin(15, Pin.OUT)
# O ID -1 cria um timer virtual no MicroPython
timer = Timer(-1)

# Função de Callback (ISR)
def timer_callback(t):
    led.toggle()
    estado = "ON" if led.value() else "OFF"
    print("LED: %s" % estado)

# Inicializa timer de 500ms
timer.init(period=500, 
           mode=Timer.PERIODIC, 
           callback=timer_callback)

while True:
    machine.idle()

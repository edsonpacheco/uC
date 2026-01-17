from machine import Pin, Timer
import machine

led = Pin(15, Pin.OUT)
timer = Timer(-1)
rapido = True

def alternar_velocidade(t):
    #uso de global para acessar a variável
    # GLOBAL, declarada na inicialização, fora
    # de qualquer função
    global rapido
    rapido = not rapido
    # Define o próximo intervalo
    novo_tempo = 100 if rapido else 1000
    
    # Reconfigura o timer para o próximo ciclo
    timer.init(period=novo_tempo, 
               mode=Timer.PERIODIC, 
               callback=alternar_velocidade)
    led.toggle()

# Inicialização a 500ms
timer.init(period=500, mode=Timer.PERIODIC, 
           callback=alternar_velocidade)

while True:
    machine.idle()

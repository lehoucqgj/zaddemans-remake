import machine
import utime
from machine import I2C, Pin
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

# Constants
I2C_ADDR = 0x20
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

# LCD setup
i2c = I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

# Define buttons and corresponding prices
buttons = {18: 1.5,     # fret
           17: 2,       # sparta, water
           16: 2.5,     # jupiler, fris
           19: 3,       # export, fruitbier
           12: 3.5,     # gust, wijn, sportzot
           13: 4,       # cava
           14: 4.5,     # duvel, karmeliet, rouge
           15: 8        # cocktail
           }

button_pins = {pin: machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_DOWN) for pin in buttons}

button_reset = Pin(10, Pin.IN, Pin.PULL_DOWN)

# Interrupt handler
def button_irq(pin):
    #utime.sleep_ms(50)  # Debounce delay
    for pin_num, price in buttons.items():
        if button_pins[pin_num].value():  # Check which button is pressed
            print_total(update_total(price))
            break

def button_reset_irq(pin):
    if pin == button_reset and button_reset.value() == 1:
        reset()

total = 0.0
def update_total(price):
    global total
    total += price
    return total

def button_activation():
    for pin_num, pin_obj in button_pins.items():
        pin_obj.irq(trigger=machine.Pin.IRQ_RISING, handler=button_irq)

    button_reset.irq(trigger=Pin.IRQ_RISING, handler=button_reset_irq)
def button_deactivation():
    for pin_num, pin_obj in button_pins.items():
        pin_obj.irq(handler=None)


def print_total(toprint):
    global total
    start_time = utime.ticks_ms() #Time recording start

    # Clear the area where the total is displayed
    for i in range(9, 16):
        lcd.move_to(i, 0)
        lcd.putchar(' ')
    
    if toprint < 10:
        position = 12
    elif toprint < 100:
        position = 11
    elif toprint < 1000:
        position = 10
    else:
        position = 9
    
    lcd.move_to(position, 0)
    lcd.putstr("{:.2f}".format(toprint))

    end_time = utime.ticks_ms() #Time recording end
    execution_time = utime.ticks_diff(end_time, start_time)  # Calculate the difference
    print("Execution time: {} miliseconds".format(execution_time))


def welcome():
    button_deactivation()
    # begroeting
    lcd.clear()
    lcd.putstr("Jow zadde")
    lcd.move_to(4, 1)
    lcd.putstr("fluidde")
    utime.sleep(2)
    lcd.clear()

def UI():
    lcd.move_to(2, 0)
    lcd.putstr("Totaal: ")
    print_total(0.0)
    lcd.move_to(0, 1)
    lcd.putstr("Piews")
    lcd.move_to(6, 1)
    lcd.putstr("Gust")
    lcd.move_to(11, 1)
    lcd.putstr("Coca")
    button_activation()

def reset():
    global total
    total = 0.0
    lcd.clear()
    UI()

# Initialize the LCD with welcome message and UI
welcome()
UI()
# Program loop
while True:
    utime.sleep(0.001)
from machine import Pin, I2C, PWM
from pico_i2c_lcd import I2cLcd
import utime


# Piny encodera
clk = Pin(15, Pin.IN, Pin.PULL_UP) #obrót
dt  = Pin(14, Pin.IN, Pin.PULL_UP)
sw = Pin(13, Pin.IN, Pin.PULL_UP) # przycisk

# Pin led
led = Pin(16, Pin.OUT)


# Piny wyświetlacza

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
lcd = I2cLcd(i2c, 39, 2, 16)



# Piny przycisków
btn_blue = Pin(9,  Pin.IN, Pin.PULL_DOWN)
btn_green = Pin(10,  Pin.IN, Pin.PULL_DOWN)
btn_yellow = Pin(11,  Pin.IN, Pin.PULL_DOWN)
btn_red = Pin(12,  Pin.IN, Pin.PULL_DOWN)




# Buzzer
buzzer = PWM(Pin(17))
buzzer.duty_u16(0)

plant_code="3142132"
MAX_LEN = 7
digits = ""
position = 0
last_clk = clk.value()
led.value(0)
last_beep = 0
led_on = False
planting = False
last_time = utime.ticks_ms()



def tone(freq, ms):
    if freq <= 0:
        buzzer.duty_u16(0)
        utime.sleep_ms(ms)
    else:
        buzzer.freq(freq)
        buzzer.duty_u16(49152)  
        utime.sleep_ms(ms)
        buzzer.duty_u16(0)
        
        
def refresh_lcd():
    
    
    left_stars = MAX_LEN - len(digits)
    if left_stars < 0:
        left_stars = 0
    line = (" " * 4)+ ("*" * left_stars) + digits
    try:
        lcd.clear()
        lcd.putstr(line)
    except Exception:
        pass

def read_button():
    global last_beep
    now = utime.ticks_ms()

  
    cooldown = 150  

  
    can_beep = utime.ticks_diff(now, last_beep) > cooldown

    # sprawdź przyciski
    if btn_blue.value():
        if can_beep:
            tone(1600, 100)
            last_beep = now
        return "4"

    if btn_green.value():
        if can_beep:
            tone(1600, 100)
            last_beep = now
        return "3"

    if btn_yellow.value():
        if can_beep:
            tone(1600, 100)
            last_beep = now
        return "2"

    if btn_red.value():
        if can_beep:
            tone(1600, 100)
            last_beep = now
        return "1"

    return None



def countdown(sec):
    global last_time, led_on
    for i in range(sec, 0, -1):
        t = i / (sec - 1)
        if btn_red.value():
            lcd.clear()
            lcd.putstr("   CANCELED")
            tone(400, 300)
            return True

        lcd.clear()
        lcd.putstr("  WARNING! BOMB")
        lcd.move_to(0,1)
        lcd.putstr(f"     {i:2d} sek")

        if i <= 10:
            freq = 2900
            dur  = 30
        else:
            freq = 1900
            dur  = 60
            
            
        if utime.ticks_diff(utime.ticks_ms(), last_time) > dur:
            led_on = not led_on
            led.value(1 if led_on else 0)
            last_time = utime.ticks_ms()
        tone(freq, dur)
        utime.sleep_ms(750-dur)

    # Finał
    lcd.clear()
    lcd.putstr("   KABOOM!")
    for _ in range(40):
        tone(2900, 45)
        utime.sleep_ms(45)
    lcd.move_to(0,1)
    planting = False
    led.value(0)
    try:
        buzzer.duty_u16(0)
        led.value(0)
    except Exception:
        pass
    return True



try:
    while True:
        if not planting:
            if sw.value() == 0:  # reset
                position = 0
                print("Reset")
                utime.sleep_ms(200)
                led.value(0)
            current_clk = clk.value()
            # zmiana stanu
            if current_clk != last_clk:
                last_clk = current_clk
                if dt.value() != current_clk:
                    position += 1
                else:
                    position -= 1
 
        if position > 5 and not planting:
            tone(1600, 100)
            utime.sleep_ms(50)
            tone(1600, 100)
            planting = True
            lcd.putstr(" Start planting")
            utime.sleep_ms(700)
            lcd.clear()
            refresh_lcd()
            while planting:
                b = read_button()
                if b:
                    utime.sleep_ms(50)
                    
                    while read_button() is not None:
                        utime.sleep_ms(10)
                    digits += b
                   
                    if len(digits) > MAX_LEN:
                        digits = digits[-MAX_LEN:]
                    refresh_lcd()
                    utime.sleep_ms(200)  
                    if digits == plant_code:
                        finished = countdown(40)
                        planting = False
                        digits = ""
                        position = 0
                        refresh_lcd()
                        if finished:
                            if lcd:
                                lcd.clear()
                        break
               
                if sw.value() == 0:
                    digits = ""
                    refresh_lcd()
                    print("Reset digits")
                    utime.sleep_ms(200)

                utime.sleep_ms(10)
                
        
        
finally: # jak zatrzymam kod
    led.value(0)
    lcd.clear()
    buzzer.duty_u16(0)    




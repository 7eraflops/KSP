import board
import supervisor
import digitalio
import neopixel
import usb_cdc # type: ignore
import time

def setup_input_pin():
    """Initialize A1 as digital input"""
    pin = digitalio.DigitalInOut(board.A1)
    pin.direction = digitalio.Direction.INPUT
    pin.pull = digitalio.Pull.DOWN
    return pin

def setup_neopixel():
    """Initialize onboard NeoPixel"""
    return neopixel.NeoPixel(board.NEOPIXEL, 1)

def interpret_pulse(duration):
    """Convert pulse duration to binary value"""
    # Allow for some timing tolerance (±50ms)
    if 50 <= duration <= 150:  # Around 100ms
        return b"0"
    elif 250 <= duration <= 350:  # Around 300ms
        return b"1"
    else:
        return "E"  # Error case, invalid duration

def main():
    # Initialize hardware
    signal_in = setup_input_pin()
    pixel = setup_neopixel()
    data = usb_cdc.data
    
    # Variables to track signal timing
    last_state = signal_in.value
    pulse_start = None
    debounce_time = 0.01  # 10ms debounce
    last_change = time.monotonic()
    
    while True:
        current_time = time.monotonic()
        current_state = signal_in.value
        
        # Debounce and detect state changes
        if current_state != last_state and (current_time - last_change) > debounce_time:
            last_change = current_time
            
            if current_state:  # Rising edge
                pulse_start = current_time
                pixel.fill((0, 255, 0))  # Green when signal is HIGH
            else:  # Falling edge
                if pulse_start is not None:
                    duration = current_time - pulse_start
                    # Convert duration to milliseconds and interpret
                    pulse_type = interpret_pulse(duration * 1000)
                    if pulse_type != "E":  # Only output valid pulses
                        data.write(pulse_type)
                    pulse_start = None
                pixel.fill((0, 0, 0))    # Off when signal is LOW
            
            last_state = current_state
        
        # Small delay to prevent overwhelming the system
        time.sleep(0.001)  # 1ms polling rate

if __name__ == "__main__":
    main()
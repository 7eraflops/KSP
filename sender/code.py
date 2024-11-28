import board
import supervisor
import usb_cdc
import digitalio
import time

# Define the unit length in milliseconds
UNIT_LENGTH_MS = 50

def setup_usb_serial():
    """Initialize USB serial communication"""
    # Wait until serial connection is established
    while not supervisor.runtime.serial_connected:
        pass
    print("USB Serial connected!")

def setup_output_pin():
    """Initialize A3 as digital output"""
    pin = digitalio.DigitalInOut(board.A3)
    pin.direction = digitalio.Direction.OUTPUT
    return pin

def read_usb_data():
    """Read data from USB serial if available"""
    if supervisor.runtime.serial_bytes_available:
        # Read the incoming data
        data = input().strip()
        return data
    return None

def generate_pulse(pin, duration_ms):
    """Generate a single pulse with specified duration in milliseconds"""
    pin.value = True
    time.sleep(duration_ms / 1000)
    pin.value = False

def process_sequence(pin, sequence, unit_length_ms):
    """Process a sequence of pulses with given unit length"""
    for char in sequence:
        if char == '0':  # Dot: 1 unit
            print("Generating dot")
            generate_pulse(pin, unit_length_ms)
        elif char == '1':  # Dash: 3 units
            print("Generating dash")
            generate_pulse(pin, 3 * unit_length_ms)
        elif char == ' ':  # Pause between letters: 3 units
            print("Pause between letters")
            time.sleep(3 * unit_length_ms / 1000)
        elif char == '|':  # Pause between words: 7 units
            print("Pause between words")
            time.sleep(7 * unit_length_ms / 1000)
        else:
            print(f"Invalid character in sequence: {char}")
            return False
        # Pause of 1 unit between parts of a letter (dot/dash)
        if char in '01':
            time.sleep(unit_length_ms / 1000)
    return True

def main():
    # Initialize USB serial communication
    setup_usb_serial()
    
    # Initialize output pin
    output_pin = setup_output_pin()
    print("A3 pin initialized as output")
    print("Commands:")
    print("'0' - Dot (1 unit)")
    print("'1' - Dash (3 units)")
    print("' ' - Pause between letters (3 units)")
    print("'|' - Pause between words (7 units)")
    print("Example: '101 | 01 0'")

    while True:
        # Check for incoming data
        received_data = read_usb_data()
        
        if received_data is not None:
            print(f"Received: {received_data}")
            # Process sequence
            print(f"Processing sequence: {received_data}")
            if process_sequence(output_pin, received_data, UNIT_LENGTH_MS):
                print("Sequence completed")
            else:
                print("Invalid sequence. Please use '0', '1', ' ', and '|' only")

if __name__ == "__main__":
    main()

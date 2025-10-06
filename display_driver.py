"""
OLED display driver for SSD1309 screen.
"""
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1309
from PIL import ImageFont
import time


class DisplayDriver:
    """
    Driver for SSD1309 OLED display.
    """
    
    def __init__(self, port=1, address=0x3C, width=128, height=64, rotate=0):
        """
        Initialize the OLED display.
        
        Args:
            port (int): I2C port number
            address (int): I2C address of the display
            width (int): Display width in pixels
            height (int): Display height in pixels
            rotate (int): Rotation angle (0, 1, 2, or 3)
        """
        try:
            serial = i2c(port=port, address=address)
            self.device = ssd1309(serial, width=width, height=height, rotate=rotate)
            self.width = width
            self.height = height
            self.is_on = True
        except Exception as e:
            print(f"Warning: Could not initialize display: {e}")
            print("Running in headless mode (display output disabled)")
            self.device = None
            self.width = width
            self.height = height
            self.is_on = True
    
    def turn_on(self):
        """Turn the display on."""
        if self.device:
            self.device.show()
            self.is_on = True
    
    def turn_off(self):
        """Turn the display off."""
        if self.device:
            self.device.hide()
            self.is_on = False
    
    def clear(self):
        """Clear the display."""
        if self.device:
            self.device.clear()
    
    def display_metrics(self, nodes_data):
        """
        Display metrics from all nodes on the OLED screen.
        
        Args:
            nodes_data (dict): Dictionary containing metrics for each node
        """
        if not self.device or not self.is_on:
            return
        
        with canvas(self.device) as draw:
            y = 0
            line_height = 16
            
            # Sort nodes to ensure consistent order
            sorted_nodes = sorted(nodes_data.items())
            
            for node_name, metrics in sorted_nodes:
                if metrics is None:
                    # Node is offline
                    text = f"{node_name}: OFFLINE"
                    draw.text((0, y), text, fill="white")
                else:
                    # Display node info: hostname, CPU%, MEM%, TEMP
                    hostname = metrics.get('hostname', 'N/A')[:10]
                    cpu = metrics.get('cpu_percent')
                    mem = metrics.get('memory_percent')
                    temp = metrics.get('temperature')
                    
                    # Format the line
                    cpu_str = f"{cpu:.0f}%" if cpu is not None else "N/A"
                    mem_str = f"{mem:.0f}%" if mem is not None else "N/A"
                    temp_str = f"{temp:.0f}C" if temp is not None else "N/A"
                    
                    text = f"{hostname[:8]:<8} {cpu_str:>3} {mem_str:>3} {temp_str:>4}"
                    draw.text((0, y), text, fill="white")
                
                y += line_height
    
    def display_text(self, text):
        """
        Display simple text on the screen.
        
        Args:
            text (str): Text to display
        """
        if not self.device or not self.is_on:
            return
        
        with canvas(self.device) as draw:
            draw.text((0, 0), text, fill="white")
    
    def display_loading(self):
        """Display a loading message."""
        self.display_text("Loading...")


if __name__ == '__main__':
    # Test the display driver
    print("Testing display driver...")
    
    display = DisplayDriver()
    
    # Test loading screen
    display.display_loading()
    time.sleep(2)
    
    # Test with sample data
    sample_data = {
        'node1': {
            'hostname': 'pi-node1',
            'cpu_percent': 45.2,
            'memory_percent': 62.5,
            'temperature': 52.3
        },
        'node2': {
            'hostname': 'pi-node2',
            'cpu_percent': 23.8,
            'memory_percent': 48.1,
            'temperature': 48.7
        },
        'node3': {
            'hostname': 'pi-node3',
            'cpu_percent': 67.3,
            'memory_percent': 75.2,
            'temperature': 55.9
        }
    }
    
    display.display_metrics(sample_data)
    time.sleep(5)
    
    # Test turn off/on
    print("Turning off display...")
    display.turn_off()
    time.sleep(2)
    
    print("Turning on display...")
    display.turn_on()
    display.display_metrics(sample_data)
    time.sleep(2)
    
    print("Test complete!")

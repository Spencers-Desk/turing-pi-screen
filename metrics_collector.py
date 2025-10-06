"""
Metrics collector for gathering system information from nodes.
"""
import psutil
import socket


def get_local_metrics():
    """
    Collect metrics from the local system.
    
    Returns:
        dict: Dictionary containing hostname, CPU usage, memory usage, and temperature
    """
    metrics = {}
    
    # Get hostname
    metrics['hostname'] = socket.gethostname()
    
    # Get CPU usage percentage
    metrics['cpu_percent'] = psutil.cpu_percent(interval=1)
    
    # Get memory usage
    memory = psutil.virtual_memory()
    metrics['memory_percent'] = memory.percent
    metrics['memory_used_mb'] = memory.used // (1024 * 1024)
    metrics['memory_total_mb'] = memory.total // (1024 * 1024)
    
    # Get CPU temperature (try different methods for Raspberry Pi)
    metrics['temperature'] = get_cpu_temperature()
    
    return metrics


def get_cpu_temperature():
    """
    Get CPU temperature for Raspberry Pi.
    
    Returns:
        float: Temperature in Celsius, or None if unavailable
    """
    try:
        # Try thermal zone (works on Raspberry Pi)
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = float(f.read().strip()) / 1000.0
            return round(temp, 1)
    except (FileNotFoundError, PermissionError, ValueError):
        pass
    
    try:
        # Try psutil sensors_temperatures (if available)
        temps = psutil.sensors_temperatures()
        if temps:
            # Try to find CPU temperature
            for name, entries in temps.items():
                if 'cpu' in name.lower() or 'coretemp' in name.lower():
                    if entries:
                        return round(entries[0].current, 1)
    except (AttributeError, KeyError):
        pass
    
    return None


if __name__ == '__main__':
    # Test the metrics collector
    metrics = get_local_metrics()
    print("Local Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")

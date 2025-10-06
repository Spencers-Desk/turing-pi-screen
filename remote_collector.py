"""
Remote metrics collector using SSH to query other nodes.
"""
import paramiko
import socket
import os
from pathlib import Path


class RemoteCollector:
    """
    Collect metrics from remote nodes via SSH.
    """
    
    def __init__(self, ssh_key_file=None, timeout=5):
        """
        Initialize the remote collector.
        
        Args:
            ssh_key_file (str): Path to SSH private key file
            timeout (int): SSH connection timeout in seconds
        """
        self.ssh_key_file = ssh_key_file
        self.timeout = timeout
        
        # Expand home directory if needed
        if self.ssh_key_file:
            self.ssh_key_file = os.path.expanduser(self.ssh_key_file)
    
    def get_remote_metrics(self, host, user):
        """
        Collect metrics from a remote node.
        
        Args:
            host (str): IP address or hostname of the remote node
            user (str): SSH username
            
        Returns:
            dict: Dictionary containing metrics, or None if connection failed
        """
        try:
            # Create SSH client
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect to remote host
            if self.ssh_key_file and os.path.exists(self.ssh_key_file):
                client.connect(
                    host,
                    username=user,
                    key_filename=self.ssh_key_file,
                    timeout=self.timeout,
                    look_for_keys=True,
                    allow_agent=True
                )
            else:
                # Try default SSH keys and agent
                client.connect(
                    host,
                    username=user,
                    timeout=self.timeout,
                    look_for_keys=True,
                    allow_agent=True
                )
            
            # Execute commands to get metrics
            metrics = {}
            
            # Get hostname
            stdin, stdout, stderr = client.exec_command('hostname')
            metrics['hostname'] = stdout.read().decode().strip()
            
            # Get CPU usage
            stdin, stdout, stderr = client.exec_command(
                'top -bn1 | grep "Cpu(s)" | sed "s/.*, *\\([0-9.]*\\)%* id.*/\\1/" | awk \'{print 100 - $1}\''
            )
            try:
                metrics['cpu_percent'] = round(float(stdout.read().decode().strip()), 1)
            except ValueError:
                metrics['cpu_percent'] = None
            
            # Get memory usage
            stdin, stdout, stderr = client.exec_command(
                'free -m | grep Mem | awk \'{print $3,$2,($3/$2)*100}\''
            )
            try:
                mem_output = stdout.read().decode().strip().split()
                metrics['memory_used_mb'] = int(mem_output[0])
                metrics['memory_total_mb'] = int(mem_output[1])
                metrics['memory_percent'] = round(float(mem_output[2]), 1)
            except (ValueError, IndexError):
                metrics['memory_percent'] = None
                metrics['memory_used_mb'] = None
                metrics['memory_total_mb'] = None
            
            # Get CPU temperature
            stdin, stdout, stderr = client.exec_command(
                'cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null'
            )
            try:
                temp = float(stdout.read().decode().strip()) / 1000.0
                metrics['temperature'] = round(temp, 1)
            except ValueError:
                metrics['temperature'] = None
            
            client.close()
            return metrics
            
        except (paramiko.SSHException, socket.error, Exception) as e:
            print(f"Error connecting to {host}: {e}")
            return None
    
    def get_all_nodes_metrics(self, nodes):
        """
        Collect metrics from all configured nodes.
        
        Args:
            nodes (dict): Dictionary of node configurations
            
        Returns:
            dict: Dictionary mapping node names to their metrics
        """
        all_metrics = {}
        for node_name, node_config in nodes.items():
            metrics = self.get_remote_metrics(
                node_config['ip'],
                node_config['user']
            )
            all_metrics[node_name] = metrics
        
        return all_metrics


if __name__ == '__main__':
    # Test the remote collector
    import yaml
    
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    collector = RemoteCollector(
        ssh_key_file=config['ssh'].get('key_file'),
        timeout=config['ssh'].get('timeout', 5)
    )
    
    metrics = collector.get_all_nodes_metrics(config['nodes'])
    print("Remote Metrics:")
    for node, data in metrics.items():
        print(f"\n{node}:")
        if data:
            for key, value in data.items():
                print(f"  {key}: {value}")
        else:
            print("  Connection failed")

import paramiko
from ..constants import SSH_PRIVATE_KEY_PATH, HOST, PORT, USERNAME, NGINX_IP
import logging

logger = logging.getLogger(__name__)

class SSHManager:

    def get_ssh_client():
        ssh_client = paramiko.SSHClient()
        key = paramiko.RSAKey.from_private_key_file(SSH_PRIVATE_KEY_PATH)
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh_client.connect(HOST, PORT, USERNAME, pkey=key)
        return ssh_client


    def add_ip_table(port: int):
        if not isinstance(port, int):
            raise ValueError("Parameter 'port' must be an integer.")

        ssh_client = SSHManager.get_ssh_client()
        try:
            command = (
                f'iptables -t nat -A PREROUTING -p tcp --dport {port} '
                f'-j DNAT --to-destination {NGINX_IP}:{port}'
            )
            ssh_client.exec_command(command)
            logger.info(f"[SSHManager] Added iptables rule for port {port}")
        except Exception as e:
            logger.error(f"[SSHManager] Failed to add iptables rule for port {port}: {e}")
            raise e
        finally:
            ssh_client.close()


    def remove_ip_table(port: int):
        if not isinstance(port, int):
            raise ValueError("Parameter 'port' must be an integer.")

        ssh_client = SSHManager.get_ssh_client()
        try:
            command = (
                f'iptables -t nat -D PREROUTING -p tcp --dport {port} '
                f'-j DNAT --to-destination {NGINX_IP}:{port}'
            )
            ssh_client.exec_command(command)
            logger.info(f"[SSHManager] Removed iptables rule for port {port}")
        except Exception as e:
            logger.error(f"[SSHManager] Failed to remove iptables rule for port {port}: {e}")
        finally:
            ssh_client.close()

import paramiko
from ..constants import SSH_PRIVATE_KEY_PATH, HOST, PORT, USERNAME, NGINX_IP

class SSHManager:

    def get_ssh_client():
        ssh_client = paramiko.SSHClient()
        key = paramiko.RSAKey.from_private_key_file(SSH_PRIVATE_KEY_PATH)
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        return ssh_client.connect(HOST, PORT, USERNAME, pkey=key)


    def add_ip_table(port : int):
        ssh_client = SSHManager.get_ssh_client()
        ssh_client.exec_command(f'iptables -t nat -A PREROUTING -p tcp --dport {port} -j DNAT --to-destination {NGINX_IP}:{port}')
        ssh_client.close()
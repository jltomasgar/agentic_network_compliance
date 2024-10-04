from langchain_core.tools import BaseTool
import paramiko
import time
import os

class SSHRetriever(BaseTool):
    name: str = "SSH_Retrieve_Tool"
    description: str = "Connects to a remote device via SSH, retrieves its configuration and saves it to a file. "
    def _run(self, hostname: str, username: str, password: str, command: str) -> dict:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=hostname, username=username, password=password)
            stdin, stdout, stderr = ssh.exec_command(command)
            config_output = stdout.read().decode()
            ssh.close()
            try:
                if not os.path.exists('configs'):
                    os.makedirs('configs')
                with open("./configs/"+hostname, "w") as f:
                    f.write(config_output)
                print(f"File written to {hostname}.")
                return config_output
            except Exception:
                return "Failed to save configuration files."
        except Exception as e:
            return f"Failed to retrieve config: {str(e)}"

class SSHConfig(BaseTool):
    name: str = "SSH_Config_Tool"
    description: str = "Connects to a remote device via SSH and configures a list of commands. "
    def _run(self, hostname: str, username: str, password: str, CLI_commands: list) -> list:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=hostname, username=username, password=password)
            shell = ssh.invoke_shell()
            l_config_output = []
            for each_command in CLI_commands:
                shell.send(each_command + "\n")
                while not shell.recv_ready():
                    time.sleep(1)
                config_output = shell.recv(65535).decode()
                print(config_output+'\n')
                l_config_output = l_config_output + [config_output]
            # for each_command in CLI_commands:
            #     stdin, stdout, stderr = ssh.exec_command(each_command)
            #     config_output = stdout.read().decode()
            ssh.close()
            return l_config_output
        except Exception as e:
            return f"Failed to retrieve config: {str(e)}"


class File_writer(BaseTool):
    name: str = "File writer"
    description: str = "Writes contents to a local file. "
    def _run(self, file_name: str, contents: str) -> str:
        try:
            with open(file_name, "w") as f:
                f.write(contents)
            print(f"File written to {file_name}.")
            return contents
        except Exception:
            return "Failed to save proposed changes."

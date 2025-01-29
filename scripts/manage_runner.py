import os
import subprocess

def run_command(command):
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        exit(result.returncode)

if __name__ == "__main__":

    print("run.sh")
    run_command("run.sh")

    

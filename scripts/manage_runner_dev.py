import os
import subprocess

# Set default environment variables
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

def run_command(command):
    """Helper function to run shell commands."""
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        exit(result.returncode)

if __name__ == "__main__":
    print("Print OS...")
    run_command("uname -a")

    print("Print python...")
    run_command("python --version")

    print("Print ls...")
    run_command("ls -al")

    print("Current working directory 1:", os.getcwd())
    print("Python Path:", os.environ.get("PYTHONPATH", "Not set"))
    print("Environment variables:")
    for key, value in os.environ.items():
        print(f"{key}={value}")

    print("List current directory 1:")
    run_command("ls -al")

    print("List /:")
    run_command("ls -al /")

    print("Current working directory 2:", os.getcwd())
    run_command("pwd")

    print("run_command: cd /")
    run_command("cd /")

    print("Current working directory 3:", os.getcwd())
    run_command("pwd")

    print("List current directory 3:")
    run_command("ls -al")

    print("List scripts:")
    run_command("ls -al scripts")

    print("chdir /:")
    os.chdir("/")

    print("Current working directory 4:", os.getcwd())
    run_command("pwd")

    print("List current directory 4:")
    run_command("ls -al")

    print("chdir /app:")
    os.chdir("/app")

    print("Current working directory 5:", os.getcwd())
    run_command("pwd")

    print("List current directory 5:")
    run_command("ls -al")

    print("Waiting for the database...")
    run_command("python manage.py wait_for_db")

    print("Collecting static files...")
    run_command("python manage.py collectstatic --noinput")

    print("Applying migrations...")
    run_command("python manage.py migrate")


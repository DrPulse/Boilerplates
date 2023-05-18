import subprocess

def run_poetry_install():
    try:
        subprocess.run(["poetry", "install"], check=True)
        print("Command 'poetry install' completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running 'poetry install': {e}")

run_poetry_install()
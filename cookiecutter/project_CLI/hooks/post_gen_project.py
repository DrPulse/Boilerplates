import subprocess

def run_poetry_install():
    try:
        subprocess.run(["poetry", "install"], check=True)
        print("Command 'poetry install' completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running 'poetry install'. Check that the specified python version is installed. Error Details:\n{e}")
    except FileNotFoundError as e:
        print(f"Poetry not installed, can't install dependencies. {e}")

run_poetry_install()
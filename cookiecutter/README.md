# Cookiecutter templates

A command-line utility that creates projects from **cookiecutters** (project templates), e.g. creating a Python package project from a Python package project template.
- Documentation: [https://cookiecutter.readthedocs.io](https://cookiecutter.readthedocs.io)
- GitHub: [https://github.com/cookiecutter/cookiecutter](https://github.com/cookiecutter/cookiecutter)

## How to use templates

- Simple command line usage:

  ```bash
  # Create project from the cookiecutter-pypackage.git repo template
  # You'll be prompted to enter values.
  # Then it'll create your Python package in the current working directory,
  # based on those values.
  $ cookiecutter https://github.com/DrPulse/Boilerplates --directory cookiecutter/*template*
  # For the sake of brevity, repos on GitHub can just use the 'gh' prefix
  $ cookiecutter gh:DrPulse/Boilerplates --directory cookiecutter/*template*
  ```

- Use it at the command line with a local template:

  ```bash
  # Create project in the current working directory, from the local
  # cookiecutter-pypackage/ template
  $ cookiecutter cookiecutter-pypackage/

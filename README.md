# SHG_dev
## Sysytem Requirements
- This repository has been tested and works for the following operating systems: `Windows, macOS, Linux`
    - This repository was created on: `macOS Sonoma 14.5 M1 Pro Processor`
    - This repository was tested on: 
- Simulations will require a working internet connection, data fitting can be done offline.
- This repository use poetry as a package manager to make it easy to install all dependencies to properly execute the program. 
    - Installing and using poetry can be found below.
    - Documentation about the poetry package can be found [here](https://www.python-poetry.org).  
#### Installing Poetry  
Install poetry with pip: 
```
    pip install poetry
```
#### Create Conda Environment with Python
Conda does not need to be installed, however, it allows for local developmental enviorments.  
If user wishes to use another package manager (such as pip) for the next step, then ignore any references to conda.  
Creating a new conda enviorment:
```
    conda create --name env_name_here
    conda activate env_name_here
```
Documentation about installing conda can be found [here](https://conda.io/projects/conda/en/latest/user-guide/install/index.html).
#### Installing Packages Locally  
In the repository's directory:
```
    conda activate env_name_here
    poetry install
```
This will install all the packages needed to compile and run the program.  
All packages and versions that will be installed can be viewed in the `pyproject.toml` file under the `tool.poetry.dependencies` section.
## Running the Program  
If poetry was properly installed inside the repository, then the following script will be active and will initialize the gui:
```   
    shg_gui
```

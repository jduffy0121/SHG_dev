# SHG_dev
![GitHub release version](https://img.shields.io/github/v/release/jduffy0121/SHG_dev?color=%2350C878&include_prereleases)
![License](https://img.shields.io/github/license/jduffy0121/SHG_dev)
![GitHub Size](https://img.shields.io/github/repo-size/jduffy0121/SHG_dev)
  
The purpose of this package is to to assist the Condensed Matter Physics communitiy members who work with Rotational-Anisotropic Second-Harmonic Generation (RA-SHG).  
  
To achieve this goal, this package has two main functions: 
1. To fit collected RA-SHG data to different nonlinear crystals and point groups using an r squared fitting function.
2. To simulate RA-SHG data based on a crystal lattice for the electric dipole (ED), electric quadrupole (EQ), and magnetic dipole (MD) radiation sources.
  
*Note: This package is for academic and educational research use only (our software does not collect any data from users)*  
  
## Sysytem Requirements
- This package has been tested and works for the following operating systems: `Windows`, `macOS`, `Linux`
    - This package was created on: `macOS Sonoma 14.5 M1 Pro Processor`
    - This package was tested on: 
- Simulations will require a working internet connection, data fitting can be done offline.
- This package use poetry as a package manager as it make it easy for users to install all dependencies to properly execute the program. 
    - Installing and using poetry to run this program can be found below.
    - Documentation about the poetry package can be found [here](https://www.python-poetry.org). 
  
### Installing the Poetry Package
Install poetry with pip: 
```
pip install poetry
```
Other more advanced methods of installation can be found in the poetry documentation above.
  
### Creating a new Conda environment with Python
Conda does not need to be installed, however, it allows for an easy way to create isolated local developmental enviorments.  
If user wishes to use another package manager for their virtual environments (such as pip) for the next step, then ignore any references to conda.  
Creating a new conda enviorment:
```
conda create --name env_name_here
conda activate env_name_here
```
Documentation about installing conda can be found [here](https://conda.io/projects/conda/en/latest/user-guide/install/index.html).
  
### Installing Packages Locally  
In the repository's root directory, run:
```
poetry install
```
This will install all the packages needed to compile and run the program.  
All packages and versions of these packages that will be installed can be viewed in the `pyproject.toml` file under the `tool.poetry.dependencies` section.
  
## Running the Program  
If poetry was properly installed inside the repository, then the following script will be active and will initialize the gui:
```   
shg_gui
```
*Note: this script must be performed in the root directory of the repository*
  
## Update History
None yet, this package still in developmental stage.
  
## About Us
This package was created by the [Ultrafast Nonlinear Optics (UNO)](https://jinlab.auburn.edu/) at Auburn University's Physics Department.  
  
Specific member contributors:
- Jacob Duffy (Auburn University - Physics and Computer Science Departments: jod0007@auburn.edu)
- Hussam Mustafa (Auburn University – Physics Department: hnm0037@auburn.edu)
- Brian Opatosky (Auburn University – Physics Department: bbo0007@auburn.edu)
- Chunli Tang (Auburn University – Electrical and Computer Engineering Department: chunli.tang@auburn.edu)
  
We would like to thank our advisor for the support in creating this package:
- [Dr. Wencan Jin](https://www.auburn.edu/cosam/departments/physics/physics-faculty/jin/index.htm) (Auburn University – Physics Department: wjin@auburn.edu)

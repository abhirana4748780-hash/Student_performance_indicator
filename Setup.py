HYPEN_E_DOT = '-e .'

def get_requirements(file_path:str)->List[str]:
    """
    This function will return the list of requirements mentioned in the requirements.txt file

    Args:
        file_path (str): The path to the requirements.txt file

    Returns:
        List[str]: A list of requirements
    """
    requirements = []
    with open(file_path) as file_object:
        requirements = file_object.readlines()
        requirements = [req.replace("\n","") for req in requirements]


        if HYPEN_E_DOT in requirements:
            requirements.remove(HYPEN_E_DOT)

    return requirements


from setuptools import find_packages,setup
from typing import List

setup(
    name = 'Student_Performance_Indicator',
    version = '0.0.1',
    author= ' Abhinav Chauhan',
    author_email= 'abhirana4748780@gmail.com',
    packages = find_packages(),
    install_requires = get_requirements("requirements.txt")
)
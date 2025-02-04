from setuptools import find_packages,setup
from typing import List
# This setup can be considered as the metadata for the ml program ->
HYPEN_E_DOT='-e .'
def get_requirements(file_path : str)->List[str]:
    # this finction will return the list of the requirements
    with open(file_path) as file_obj:
        requirements=file_obj.readlines()
        [req.replace("\n","") for req in requirements]

        if HYPEN_E_DOT in requirements:
            requirements.remove(HYPEN_E_DOT)
    return requirements
setup(
    name='mlproject',
    version='0.0.1',
    author='Suyash',
    author_email='suyash123sj.01@gmail.com',
    packages=find_packages(),
    install_requires=get_requirements('requirements.txt')
)
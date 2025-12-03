"""
Setup script para py-strava.

Este script permite instalar el proyecto y crear el comando 'strava'
que estará disponible en el PATH del sistema.

Instalación en modo desarrollo:
    pip install -e .

Instalación normal:
    pip install .
"""

from setuptools import setup, find_packages
from pathlib import Path

# Leer el contenido del README
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ''

# Leer dependencias del requirements.txt
requirements_file = Path(__file__).parent / 'requirements.txt'
requirements = []
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith('#')
        ]

setup(
    name='py-strava',
    version='2.2.0',
    description='Sincroniza y analiza actividades de Strava',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Strava Analytics Team',
    author_email='',
    url='https://github.com/tu-usuario/py-strava',
    packages=find_packages(exclude=['tests', 'tests.*', 'scripts', 'docs']),
    include_package_data=True,
    install_requires=requirements,
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'strava=py_strava.cli.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    keywords='strava api sync activities sports analytics',
    project_urls={
        'Documentation': 'https://github.com/tu-usuario/py-strava/docs',
        'Source': 'https://github.com/tu-usuario/py-strava',
        'Tracker': 'https://github.com/tu-usuario/py-strava/issues',
    },
)

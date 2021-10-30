from setuptools import setup, find_packages
import os 

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name = 'booknote',
    version = '1.0',
    author = 'Pedro Henrique Limeira da Cruz',
    author_email = 'pedrohlcruz@gmail.com',
    license = 'MIT',
    description = "Command Line Interface to upload kindle's highlights to a Notion Page with custom formatting",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'https://github.com/Pedro4064/Kindle_Notion',
    py_modules = ['booknote_cli', 'booknote'],
    packages = find_packages(),
    install_requires = [requirements],
    python_requires='>=3.5',
    include_package_data=True,

    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ],

    entry_points = '''
        [console_scripts]
        booknote=booknote_cli:cli
    '''
)

# After Initial package setup create the booknote/ directory in ~/.config
try:
    os.mkdir(os.path.expanduser("~") + "/.config/booknote")
except FileExistsError:
    print("[WARNIGN] ~/.config/booknote directory already exists")
except Exception as e:
    print(e)
    exit(1)
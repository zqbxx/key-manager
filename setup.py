# coding=utf-8

from setuptools import setup, find_packages
from io import StringIO, open
import fnmatch
from setuptools.command.build_py import build_py as build_py_orig
import os


def read_file(filename):
    with open(filename, 'r', encoding='UTF-8') as fp:
        return fp.read().strip()


def read_requirements(filename):
    return [line.strip() for line in read_file(filename).splitlines()
            if not line.startswith('#')]


def read_README(filename):
    # Ignore unsupported directives by pypi.
    content = read_file(filename)
    return ''.join(line for line in StringIO(content)
                   if not line.startswith('.. comment::'))


# excluded = ['test/*.py']

excluded = []

def filter_py_file(item):
    print(item)
    return False

class build_py(build_py_orig):

    def find_package_modules(self, package, package_dir):
        modules = super().find_package_modules(package, package_dir)
        for (pkg, mod, file) in modules:
            print(f'custom build py {pkg} - {mod} - {file}')
        return [
            (pkg, mod, file)
            for (pkg, mod, file) in modules
            if not any(fnmatch.fnmatchcase(file, pat=os.path.normpath(pattern)) for pattern in excluded)
        ]

setup(
    name="key-manager",
    version="1.0.0",
    author="wx c",
    description="密钥管理器。提供了密钥生成功能，使用aes-256加密，并提供基于pyside6的菜单和对话框组件",
    license="MIT",
    keywords="",
    url="https://github.com/zqbxx/key-manager",
    python_requires='>=3.8',
    install_requires=read_requirements('requirements.txt'),
    packages=['keymanager', 'keymanager.ui'],
    long_description=read_README('README.md'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        "Topic :: ",
        'Environment :: Console',
        'Intended Audience :: Developers',
        "License :: MIT",
        'Natural Language :: Chinese',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    zip_safe=False
)

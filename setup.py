from setuptools import setup

setup(
    name='suio',
    version='0.1.0',
    description='Python I/O module for seismic dataset with Seismic Un*x format',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Dr. Sumin Kim',
    author_email='seisminic@gmail.com',
    url='https://github.com/seismin91',
    py_modules=['suio'],
    include_package_data=True,  # 중요!
    classifiers=[
        'Programming Language :: Python :: 3',
        'Intended Audience :: Science/Research',
    ],
    python_requires='>=3.6',
    install_requires=[
        'numpy',
    ],
)

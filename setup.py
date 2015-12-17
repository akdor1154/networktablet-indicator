from setuptools import setup

setup(
    name='networktablet-indicator',
    version='1.0.0',
    description='An AppIndicator for Networktablet',
    long_description="""
An AppIndicator for Networktablet, to allow you
to use a touchscreen computer as a graphics tablet
for this computer.
""",
    url='https://github.com/akdor1154/networktablet-indicator',
    author='Jarrad Whitaker',
    author_email='akdor1154@gmail.com',
    license='MIT',
    packages=['networktablet_indicator'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Environment :: X11 Applications',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Artistic Software',
        'Topic :: Multimedia :: Graphics'
    ],
    keywords='networktablet graphics tablet wacom stylus',
    install_requires=['pyxdg'],
    entry_points={
        'console_scripts': [
            'networktablet-indicator=networktablet_indicator:main'
        ]
    }
)

from setuptools import find_packages, setup

package_name = 'dsr_example'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='gossi',
    maintainer_email='mincheol710313@gmail.com',
    description='TODO: Package description',
    license='BSD',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
                'dance = dsr_example.demo.dance_m1013:main',
                'single_robot_simple = dsr_example.simple.single_robot_simple:main',
                'slope_demo = dsr_example.demo.slope_demo:main',
                'servoj_stream_publisher = dsr_example.simple.servoj_stream_publisher:main',
                'doosan_zmq_ros2_bridge = dsr_example.simple.doosan_zmq_ros2_bridge:main',
                'doosan_outbound_zmq = dsr_example.simple.doosan_outbound_zmq:main',
        ],
    },
)

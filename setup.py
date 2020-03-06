import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='jderobot-objectdetector',  
     version='0.1',
     scripts=['jderobot-objectdetector'] ,
     author="JdeRobot",
     author_email="",
     description="dl-objectdetector is a JdeRobot node, composed of 3 entities: Camera, GUI and DetectionNetwork, which have been implemented on an asynchronous design with its own thread",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/JdeRobot/ObjectDetector",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 2",
         "Operating System :: OS Independent",
     ],
 )

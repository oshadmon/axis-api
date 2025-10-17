# Axis Demo

The following demonstrates utilizing insights from [Axis Cameras](https://www.axis.com/products/network-cameras) into 
AnyLog/EdgeLake (operator) agents. 

* [axis_demo.py](#axis_demopy)

## axis_demo.py

The script [axis_demo.py](axis_demo.py) it the main for getting insights and publishing them to AnyLog.

**Logic**
0. Whenever Axis camera software recognizes an object it sends the inference to an external MQTT broker

Once an inference is received on the MQTT broker the following actions happen on axis_demo.py:

1. The application tells the camera to take a screenshot 
2. It merges the inference with the snapshot 
3. publish everything into AnyLog via REST (POST). 


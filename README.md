# axis-api

The following project demonstrates communicating with VideoBank (Axis Cameras) and pushing it to AnyLog/EdgeLake. 

**Docs**: https://developer.axis.com/

## requirements 
* flask 
* requests 
* xmltodict

## Flask App
1. For [camera_actions](camera_actions.py) camera connection information. This can be done as an 
environment variable called `CAMERA_CONN` - Format: `USER:PASSWORD@IP:PORT`
 
2. **Run Application** - URL: http://127.0.0.1:5000  
```shell
python3 camera_actions.py
```

3. Using browser execute requests

<div align="center">

|           Call            |                          Info                     | 
|:-------------------------:|:-------------------------------------------------:| 
|     `/config/status`      |        get camera status (active / not active)    | 
|      `/config/info`       |              get information about camera         | 
|   `/config/geolocation`   |                  get camera location              | 
|        `/app/list`        |         list of application "installed" names     |
| `/app/<app_name>/status`  |   status for a specific application (based on name) |
|  `/app/<app_name>/info`   |  information regarding a specific app (based on name) |
|  `/app/<app_name>/start`  |           start application  (based on name)      | 
|  `/app/<app_name>/stop`   |            stop application (based on name)       | 
| `/app/<app_name>/restart` |          restart application (based on name)      | 
| `/app/<app_name>/remove`  |           remove application (based on name)      |
| `/recordings/list` |               list accessible recordings          | 
| `/recordings/<record_id>` | get information for a specific recording (based on ID) |
| `/recordings/export/<record_id>` |        export recording based on recording ID     |

</div>
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

## Preparing AnyLog

In order to accept data into AnyLog user needs to declare a mapping policy and MQTT client; this can be done via 
[anylog_operator.py](anylog_operator.py). This step is to be done each time node reboots. The policy does not get 
regenerated each time though. 

```shell
python3 anylog_operator.py [OPERATOR CONN] [LEDGER_CONN] {--topic [axis]}
```

**Behavior**:
```anylog 
AL anylog-operator > blockchain get mapping 

[{'mapping' : {'id' : 'axis',
               'dbms' : 'bring [dbms]',
               'table' : 'bring [table]',
               'video_id' : 'bring [video_id]',
               'timestamp' : {'type' : 'timestamp',
                              'default' : 'now()'},
               'start_time' : {'type' : 'timestamp',
                               'bring' : '[start_time]'},
               'end_time' : {'type' : 'timestamp',
                             'bring' : '[end_time]'},
               'source' : {'type' : 'string',
                           'bring' : '[source]'},
               'file_type' : {'type' : 'string',
                              'bring' : '[file_type]'},
               'file' : {'blob' : True,
                         'bring' : '[content]',
                         'extension' : 'mp4',
                         'apply' : 'base64decoding',
                         'hash' : 'md5',
                         'type' : 'varchar'},
               'readings' : 'video',
               'schema' : {'video_resolution' : {'type' : 'string',
                                                 'bring' : '[resolution]'},
                           'video_width' : {'type' : 'string',
                                            'bring' : '[width]'},
                           'video_height' : {'type' : 'string',
                                             'bring' : '[height]'}},
               'date' : '2025-09-23T19:46:42.240825Z',
               'ledger' : 'global'}}]

AL anylog-operator > get msg client 

Subscription ID: 0001
User:         unused
Broker:       rest
Connection:   Connected to local Message Server

     Messages    Success     Errors      Last message time    Last error time      Last Error
     ----------  ----------  ----------  -------------------  -------------------  ----------------------------------
              0           0           0  
     
     Subscribed Topics:
     Topic QOS DBMS Table Column name Column Type Mapping Function Optional Policies                                              
     -----|---|----|-----|-----------|-----------|----------------|--------|-----------------------------------------------------|
     axis |  0|    |     |           |           |                |        |blockchain get (mapping,transform) where [id] == axis|
```

## Publish Data

 
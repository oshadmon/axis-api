import datetime
import random
import time

import __support__
import __anylog_support__

def __create_policy(policy):
    new_policy = {
        "mapping": {
            "id": policy,
            "name": policy,
            "dbms": "axis",
            "table": "test",
            "schema": {
                "timestamp": {
                    "type": "timestamp",
                    "bring": "[timestamp]",
                    "default": "now()"
                },
                "value": {
                    "type": "bool",
                    "bring": "[value]",
                    "default": False
                }
            }
        }
    }

    return new_policy


def main():
    anylog_conn = '10.0.0.78:7849'
    policy = "bool-bug"

    is_policy = __support__.check_policy(anylog_conn=anylog_conn, where_condition={"id": policy})
    if not is_policy:
        new_policy = __create_policy(policy=policy)
        __anylog_support__.declare_policy(raw_policy=new_policy, anylog_conn=anylog_conn, use_ledger=False)

    if not __anylog_support__.check_mqtt(anylog_conn=anylog_conn, topic=policy):
        __anylog_support__.declare_mqtt_request(anylog_conn=anylog_conn, broker='rest',
                                                topic=f"topic=(name={policy} and policy={policy})")

    while True:
        data = {
            "dbms": "axis",
            "table": "test",
            "timestamp": datetime.datetime.now(tz=datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f'),
            "value": random.choice([True, False])
        }

        __anylog_support__.publish_data(anylog_conn=anylog_conn, payload=data, topic=policy)
        time.sleep(5)

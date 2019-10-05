# -*- coding: utf-8 -*-

import json


def handler(event, context):
    return {
        "status_code": "200",
        "body": json.dumps(event["a"] + event["b"])
    }

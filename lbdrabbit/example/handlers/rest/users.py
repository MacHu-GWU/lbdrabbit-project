# -*- coding: utf-8 -*-

from lbdrabbit.config_inherit import LbdFuncConfig

__lbd_func_config__ = LbdFuncConfig(
    lbd_func_timeout=30,
)

users = {
    "uid_1": {"user_id": "uid_1", "name": "Alice"},
    "uid_2": {"user_id": "uid_2", "name": "Bob"},
    "uid_3": {"user_id": "uid_3", "name": "Cathy"},
}


def get(event, context):
    return list(users.values())


def post(event, context):
    if event["user_id"] not in users:
        users[event["user_id"]] = event
    return "Failed! user_id = '{}' already exists.".format(event["user_id"])


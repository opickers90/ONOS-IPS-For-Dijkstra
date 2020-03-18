import requests
import logging
import json
from requests.auth import HTTPBasicAuth
from isp_config import *


# For GET REST API
def get_json(url):
    try:
        req = requests.get(url, auth=HTTPBasicAuth(ONOS_USER, ONOS_PASS))
        return req.json()
    except IOError as e:
        logging.error(e)
        return ''


# For POST REST API
def post_json(url, json_data):
    try:
        headers = {'content-type': 'application/json'}
        req = requests.post(url, data=json.dumps(json_data), headers=headers, auth=HTTPBasicAuth(ONOS_USER, ONOS_PASS))
        return req
    except IOError as e:
        logging.error(e)
        return ''


# For DELETE REST API
def del_json(url):
    try:
        req = requests.delete(url, auth=HTTPBasicAuth(ONOS_USER, ONOS_PASS))
        return req
    except IOError as e:
        logging.error(e)
        return ''


# Post Intents to Intents API
def intent_p2p_install(port_in, device_in, port_en, device_en, priority=100):
    data = {
        "type": "PointToPointIntent",
        "appId": "org.onosproject.cli",
        "resources": [],
        "selector": {
            "criteria": []
        },
        "treatment": {
            "instructions": [
                {
                    "type": "NOACTION"
                }
            ],
            "deferred": []
        },
        "priority": priority,
        "constraints": [],
        "ingressPoint": {
            "port": port_in,
            "device": device_in
        },
        "egressPoint": {
            "port": port_en,
            "device": device_en
        }
    }

    post_intent = post_json("http://{ip}:{port}/onos/v1/intents".format(ip=ONOS_IP, port=ONOS_PORT), data)
    return post_intent


def intent_m2sp_install(port1_in, device1_in, port2_in, device2_in, port_en, device_en, priority=100):
    data = {
        "type": "MultiPointToSinglePointIntent",
        "appId": "org.onosproject.cli",
        "resources": [],
        "selector": {
            "criteria": []
        },
        "treatment": {
            "instructions": [
                {
                    "type": "NOACTION"
                }
            ],
            "deferred": []
        },
        "priority": priority,
        "constraints": [],
        "ingressPoint": [
            {
                "port": port1_in,
                "device": device1_in
            },
            {"port": port2_in,
             "device": device2_in
             }
        ],
        "egressPoint": {
            "port": port_en,
            "device": device_en
        }
    }

    post_intent = post_json("http://{ip}:{port}/onos/v1/intents".format(ip=ONOS_IP, port=ONOS_PORT), data)
    return post_intent


def intent_s2mp_install(port_in, device_in, port1_en, device1_en, port2_en, device2_en, priority=100):
    data = {
        "type": "SinglePointToMultiPointIntent",
        "appId": "org.onosproject.cli",
        "resources": [],
        "selector": {
            "criteria": []
        },
        "treatment": {
            "instructions": [
                {
                    "type": "NOACTION"
                }
            ],
            "deferred": []
        },
        "priority": priority,
        "constraints": [],
        "egressPoint": [
            {
                "port": port1_en,
                "device": device1_en
            },
            {"port": port2_en,
             "device": device2_en
             }
        ],
        "ingressPoint": {
            "port": port_in,
            "device": device_in
        }
    }

    post_intent = post_json("http://{ip}:{port}/onos/v1/intents".format(ip=ONOS_IP, port=ONOS_PORT), data)
    return post_intent


# Remove Intents from Intents API
def del_intent(intent_id):
    for n in range(len(intent_id)):
        del_json("http://{ip}:{pt}/onos/v1/intents/org.onosproject.cli/{id}".format(ip=ONOS_IP, pt=ONOS_PORT,
                                                                                    id=intent_id[n]))


def remove_duplicates(lists):
    new_list = []
    for num in lists:
        if num not in new_list:
            new_list.append(num)
    return new_list

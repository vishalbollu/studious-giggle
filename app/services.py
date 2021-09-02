PRIORITY = ["low", "medium", "high", "critical"]


def empty_user():
    return {priority: {"count": 0, "incidents": []} for priority in PRIORITY}


# {
#   "results": [
#     {
#       "priority": low
#       "reported_by": 1234,
#       "timestamp": 1629939474.1346128,
#       "source_ip": "17.105.244.255"
#     }
#   ]
# }
def denial_aggregator(json_response):
    if json_response.get("results") is None:
        return {}

    response = {}

    for incident in json_response["results"]:
        incident["type"] = "denial"
        employee_id = incident["reported_by"]
        user = response.get(employee_id, empty_user())
        user[incident["priority"]]["incidents"].append(incident)
        user[incident["priority"]]["count"] += 1
        response[employee_id] = user

    return response


# {
#   "results": [
#     {
#       "priority": low,
#       "internal_ip": "17.105.244.255",
#       "timestamp": 1629939474.1346128,
#       "source_ip": "17.105.244.255"
#     }
#   ]
# }
def intrusion_aggregator(ip_address_map, json_response):
    if json_response.get("results") is None:
        return {}

    response = {}

    for incident in json_response["results"]:
        incident["type"] = "intrusion"
        employee_id = ip_address_map.get(incident["internal_ip"])
        if employee_id is None:
            continue
        user = response.get(employee_id, empty_user())
        user[incident["priority"]]["incidents"].append(incident)
        user[incident["priority"]]["count"] += 1
        response[employee_id] = user
    return response


# {
#   "results": [
#     {
#       "priority": "high",
#       "machine_ip": "17.105.244.255",
#       "timestamp": 1629939474.1346128
#     }
#   ]
# }
def executable_aggregator(ip_address_map, json_response):
    if json_response.get("results") is None:
        return {}

    response = {}

    for incident in json_response["results"]:
        incident["type"] = "executable"
        employee_id = ip_address_map.get(incident["machine_ip"])
        if employee_id is None:
            continue
        user = response.get(employee_id, empty_user())
        user[incident["priority"]]["incidents"].append(incident)
        user[incident["priority"]]["count"] += 1
        response[employee_id] = user
    return response


# {
#   "results": [
#     {
#       "priority": "low",
#       "employee_id": 447770,
#       "timestamp": 1629932993.2436273
#     },
#   ]
# }
def misuse_aggregator(json_response):
    if json_response.get("results") is None:
        return {}

    response = {}

    for incident in json_response["results"]:
        incident["type"] = "misuse"
        employee_id = incident["employee_id"]
        user = response.get(employee_id, empty_user())
        user[incident["priority"]]["incidents"].append(incident)
        user[incident["priority"]]["count"] += 1
        response[employee_id] = user
    return response


# {
#   "results": [
#     {
#       "priority": "critical",
#       "employee_id": 656611,
#       "timestamp": 1629930924.6406548
#     },
#   ]
# }
def unauthorized_aggregator(json_response):
    if json_response.get("results") is None:
        return {}

    response = {}

    for incident in json_response["results"]:
        incident["type"] = "unauthorized"
        employee_id = incident["employee_id"]
        user = response.get(employee_id, empty_user())
        user[incident["priority"]]["incidents"].append(incident)
        user[incident["priority"]]["count"] += 1
        response[employee_id] = user

    return response


# {
#   "results": [
#     {
#       "priority": "critical",
#       "ip": "17.229.47.234",
#       "timestamp": 1629933416.6438653
#     }
#   ]
# }
def probing_aggregator(ip_address_map, json_response):
    if json_response.get("results") is None:
        return {}

    response = {}

    for incident in json_response["results"]:
        incident["type"] = "probing"
        employee_id = ip_address_map.get(incident["ip"])
        if employee_id is None:
            continue
        user = response.get(employee_id, empty_user())
        user[incident["priority"]]["incidents"].append(incident)
        user[incident["priority"]]["count"] += 1
        response[employee_id] = user

    return response


# {
#   "results": [
#     {
#       "priority": "high",
#       "identifier": 243617,
#       "timestamp": 1629932888.644877
#     }
#   ]
# }
def other_aggregator(json_response):
    if json_response.get("results") is None:
        return {}

    response = {}

    for incident in json_response["results"]:
        incident["type"] = "other"
        employee_id = incident["identifier"]
        user = response.get(employee_id, empty_user())
        user[incident["priority"]]["incidents"].append(incident)
        user[incident["priority"]]["count"] += 1
        response[employee_id] = user

    return response


def zip_incidents(left_incidents, right_incidents):
    total_incidents = []

    left_idx = 0
    right_idx = 0

    while left_idx < len(left_incidents) or right_idx < len(right_incidents):
        if left_idx == len(left_incidents):
            total_incidents.append(right_incidents[right_idx])
            right_idx += 1
        elif right_idx == len(right_incidents):
            total_incidents.append(left_incidents[left_idx])
            left_idx += 1
        elif left_incidents[left_idx]["timestamp"] < right_incidents[right_idx]["timestamp"]:
            total_incidents.append(left_incidents[left_idx])
            left_idx += 1
        else:
            total_incidents.append(right_incidents[right_idx])
            right_idx += 1

    return total_incidents


def in_place_merge_incidents(left_employees, right_employees):
    right_side_only_keys = set(right_employees.keys()) - set(left_employees.keys())

    for left_key, left_employee in left_employees.items():
        if left_key in right_employees:
            right_employee = right_employees[left_key]
            for priority in PRIORITY:
                left_employee[priority]["count"] += right_employee[priority]["count"]
                left_employee[priority]["incidents"] = zip_incidents(
                    left_employee[priority]["incidents"], right_employee[priority]["incidents"]
                )

    for right_key in right_side_only_keys:
        left_employees[right_key] = right_employees[right_key]

    return left_employees

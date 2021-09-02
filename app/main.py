from fastapi import FastAPI
import asyncio
import aiohttp
import os
import services

app = FastAPI()

USERNAME = os.environ["ELEVATE_USERNAME"]
PASSWORD = os.environ["ELEVATE_PASSWORD"]

if USERNAME == "":
    raise Exception("environment variable ELEVATE_USERNAME was not specified")

if PASSWORD == "":
    raise Exception("environment variable ELEVATE_PASSWORD was not specified")


SERVICES = [
    {
        "name": "denial",
        "url": "https://incident-api.use1stag.elevatesecurity.io/incidents/denial/",
    },
    {
        "name": "intrusion",
        "url": "https://incident-api.use1stag.elevatesecurity.io/incidents/intrusion/",
    },
    {
        "name": "executable",
        "url": "https://incident-api.use1stag.elevatesecurity.io/incidents/executable/",
    },
    {
        "name": "misuse",
        "url": "https://incident-api.use1stag.elevatesecurity.io/incidents/misuse/",
    },
    {
        "name": "unauthorized",
        "url": "https://incident-api.use1stag.elevatesecurity.io/incidents/unauthorized/",
    },
    {
        "name": "probing",
        "url": "https://incident-api.use1stag.elevatesecurity.io/incidents/probing/",
    },
    {
        "name": "other",
        "url": "https://incident-api.use1stag.elevatesecurity.io/incidents/other/",
    },
    {
        "name": "identities",
        "url": "https://incident-api.use1stag.elevatesecurity.io/identities/",
    },
]


async def async_requester(session, service_def):
    try:
        async with session.get(url=service_def["url"]) as response:
            resp = await response.json()
            return (service_def["name"], resp)
    except Exception as e:
        return (service_def["name"], {})


async def parallel_requests(services):
    async with aiohttp.ClientSession(
        auth=aiohttp.BasicAuth(USERNAME, password=PASSWORD)
    ) as session:
        ret = await asyncio.gather(
            *[async_requester(session, service_def) for service_def in services]
        )
    return ret


@app.get("/incidents")
async def incidents():
    parallel_results = await parallel_requests(SERVICES)

    merged_results = {name: results for name, results in parallel_results}

    ip_address_map = merged_results["identities"]
    incidents = [
        services.denial_aggregator(merged_results["denial"]),
        services.intrusion_aggregator(ip_address_map, merged_results["intrusion"]),
        services.executable_aggregator(ip_address_map, merged_results["executable"]),
        services.misuse_aggregator(merged_results["misuse"]),
        services.unauthorized_aggregator(merged_results["unauthorized"]),
        services.probing_aggregator(ip_address_map, merged_results["probing"]),
        services.other_aggregator(merged_results["other"]),
    ]

    merged_incidents = incidents[0]

    for incident_list in incidents[1:]:
        merged_incidents = services.in_place_merge_incidents(merged_incidents, incident_list)

    return merged_incidents


@app.get("/healthz")
async def healthz():
    return "ok"

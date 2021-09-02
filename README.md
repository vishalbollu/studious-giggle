# studious-giggle

## Prerequisites

docker

## Running the challenge

### Running the server
```bash
docker pull vbollu/elevate-challenge:latest

export ELEVATE_USERNAME=<USERNAME>
export ELEVATE_PASSWORD=<PASSWORD>

docker run -d --name elevate-challenge-container -e WEB_CONCURRENCY=1 -e MAX_WORKERS=1 -e ELEVATE_USERNAME=$ELEVATE_USERNAME -e ELEVATE_PASSWORD=$ELEVATE_PASSWORD -p 9000:80 vbollu/elevate-challenge:latest
```


### Query the server

```bash
# verify that the server is running
curl http://localhost:9000/healthz

curl http://localhost:9000/incidents
```

### Cleanup

```
docker rm -f elevate-challenge-container
```

### Run tests

```bash
git clone https://github.com/vishalbollu/studious-giggle.git

cd studious-giggle

./test.sh
```

## Overall approach

The general approach I considered was to run the HTTP requests in parallel (concurrently) and then group and zip the incidents.

Technically, the requests are run concurrently using aiohttp. Concurrency in Python especially when async libraries can be leveraged is likely the most optimal way to work on multiple blocking workloads at the same time. Python doesn't support true multi-threading due to the GIL, so concurrency is great way to use more of CPU cycles.

I also considered using Golang because goroutines make parallelism a lot easier. However, I wanted to give aiohttp a shot in python.

I manually wrote the grouping and zipping logic therefore I had to add some tests to get some confidence that they were correct.

There must be libraries that can already do this, I suspect libraries like pandas. However I am not familiar with pandas. I spent about 10 minutes trying to perform the same logic using pandas however I wasn't confident about the efficiency so I ended up writing it myself.

Some services returned endpoints with two ip addresses or an ip address and an id. When there was an id, I used the id. When there are multiple fields with ip addresses I used the field that yielded the most matches.

The 2 second requirement seemed impossible for me:

Just querying all of the APIs seemed to take more than 4 seconds from my machine:

I tried a few approaches:
- Python concurrency with aiohttp
- Python "parallelism" with threads
- Bash

Here is how I tested with Bash:

```bash
echo "https://incident-api.use1stag.elevatesecurity.io/incidents/denial/
https://incident-api.use1stag.elevatesecurity.io/incidents/intrusion/
https://incident-api.use1stag.elevatesecurity.io/incidents/executable/
https://incident-api.use1stag.elevatesecurity.io/incidents/misuse/
https://incident-api.use1stag.elevatesecurity.io/incidents/unauthorized/
https://incident-api.use1stag.elevatesecurity.io/incidents/probing/
https://incident-api.use1stag.elevatesecurity.io/incidents/other/" > urls.txt

time xargs -n1 -P 7 curl -u $ELEVATE_USERNAME:$ELEVATE_PASSWORD < urls.txt
> real	0m4.143s
```

The 2 second requirement is one that I failed to achieve largely because the parallel/concurrent requests to the endpoints took longer than 2 seconds. At this point, I am assuming that there is a bottleneck in the upstream APIs which causing this delay.

Please let me know if my assumption is incorrect.

### After feedback from Jose

Jose mentioned that part of the test was to interact with upstream in a disciplined way to handle errors and timeouts, which makes sense.

After receiving the feedback, I tried adding timeouts:

```bash
echo "https://incident-api.use1stag.elevatesecurity.io/incidents/denial/
https://incident-api.use1stag.elevatesecurity.io/incidents/intrusion/
https://incident-api.use1stag.elevatesecurity.io/incidents/executable/
https://incident-api.use1stag.elevatesecurity.io/incidents/misuse/
https://incident-api.use1stag.elevatesecurity.io/incidents/unauthorized/
https://incident-api.use1stag.elevatesecurity.io/incidents/probing/
https://incident-api.use1stag.elevatesecurity.io/incidents/other/" > urls.txt

xargs -n1 -P 7 curl --max-time 2 -u $ELEVATE_USERNAME:$ELEVATE_PASSWORD < urls.txt
> real	0m2.023s

# encountered connection timed out errors without any successful responses
```

I profiled the APIs early on the challenge, each request takes about 1.5 to 1.6 seconds from Toronto (excluding the identities request). In theory, making all of these requests in parallel should result take the same amount of time as the longest request so I was expecting all of the requests to return within 1.6 seconds (approximately).

However, it seems that the more concurrent requests I make to the endpoints, the longer each individual request takes. Perhaps the upstream APIs are blocking on a shared resource? I believe this is the crux of this problem. Adding timeouts is a moot point because all of the requests will fail. Based on my interactions with the APIs it doesn't seem to be possible to scrape all of the APIs within 2 second timeframe. Perhaps a different strategy is to setup a connection pool of 2 (or 3) to only allow 2 concurrent requests and return the aggregated results.

## Production readiness checklist

Already done:
- Docker
- Use FastAPI with uvicorn and gunicorn for the uvloop and process management and graceful termination
- Healthz that can be used for readiness/liveness
- Wrote some basic unit tests

TODO:
- Add timeouts to requests made to upstream APIs
- Handle failed http requests to endpoints (return error if any requests fail, or try best-effort and communicate which upstream requests failed)
- Handle missing ip addresses
- Update the server to use structured logging (e.g. JSON) for easier analysis after exporting logs to a logging solution
- Make endpoints configurable
- If upstream endpoints are versioned, use specific versions
- Use a more standard library like pandas for grouping and joins
- Improve readiness/liveness probes to use support non-http request probes in situations where the server is encountering a high volume
- Add request tracing to make it easier to make it easier to perform RCA
- Add monitoring to observe the incoming requests to the server and metadata for each upstream API being
- Refactor code (use enums, add docstring, type hints, etc)
- Add .dockerignore to not include test files in main container

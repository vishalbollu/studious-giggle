#!/bin/bash

docker build . -f test.Dockerfile -t elevate-test && docker run elevate-test

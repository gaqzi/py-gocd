# A Python API for interacting with [Go Continuous Delivery][gocd]

The reason for this project is to provide a wrapper to easily perform operations
against Go. I've been writing a lot of shell scripts to interact with Go using
curl but when going a little further than the most basic interactions I've
always started to feel the need for doing all of this in a proper programming
language. I.e. something that is not bash.

I've chosen to use Python and version 2.6.6 as my target platform with no
external dependencies to make it really straightforward to install/run on RHEL6
and other similar stable distributions.

## Usage

This is in development and code is the final documentation for now, but the
intended usage going in is:

```python
>>> from gocd import Server
>>> server = Server('http://localhost:8153', user='ba', password='secret')
>>> pipeline = server.pipeline('Example-Pipeline')
>>> response = pipeline.history()
>>> response.status
200
>>> response.content_type
'application/json'
>>> response.is_ok  # True when pre-configured valid OK code for the endpoint
>>> response.body  # maybe it should be called payload? Properly parsed.
{"pagination":{"offset":0,"total":1,"page_size":10},"pipelines":[...]"}
```

## License
MIT License.

[gocd]: http://go.cd/

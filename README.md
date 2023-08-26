# Robot Raconteur Service Browser

This repository contains a Service Browser for Robot Raconteur to allow the user to view the available Robot Raconteur 
Services being advertised on the network to which the computer is connected. Use this tool to find the available
services and determine the connection information to use with other clients. This tool will also provide the
candidate connection URLs for the services.

Some clients have built-in discovery abilities that do not require this tool. Check the documentation for the client
you are using to see if this tool is necessary.

### Installation

Install using pip:

```
pip install robotraconteur-service-browser-gui
```

On Linux, it may be necessary to run:

```
python3 -m pip install robotraconteur-service-browser-gui
```


### Running Service Browser

The service browser can be run using the command line:

```
robotraconteur-service-browser-gui
```

Sometimes this convenience script is not in the path. Try invoking it from Python:

```
python -m robotraconteur_service_browser_gui
```

On Linux, use `python3` instead of `python`.

### Using the Service Browser

The service browser will show a list of detected URLs in a list on the top. Select one of the URLs to view the
details about the service.

### License

Apache 2.0



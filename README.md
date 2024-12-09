ABOUT
-------------------------
This is the base implementation of a full crawler that uses a spacetime
cache server to receive requests. (THIS WAS CREATED FOR AN INFORMATION RETRIEVAL CLASS AND RAN ON SUCH SERVER)

# Configuring config.ini

Set the options in the config.ini file. The following
configurations exist.

**USERAGENT**: Set the useragent to `IR F19 uci-id1,uci-id2,uci-id3`. 
It is important to set the useragent appropriately to get the credit for 
hitting our cache.

**HOST**: This is the host name of our caching server. Please set it as per spec.

**PORT**: This is the port number of our caching server. Please set it as per spec.

**SEEDURL**: The starting url that a crawler first starts downloading.

**POLITENESS**: The time delay each thread has to wait for after each download.

**SAVE**: The file that is used to save crawler progress. If you want to restart the
crawler from the seed url, you can simply delete this file.

**THREADCOUNT**: This can be a configuration used to increase the number of concurrent
threads used. Do not change it if you have not implemented multi threading in
the crawler. The crawler, as it is, is deliberately not thread safe.


# EXECUTION
-------------------------

To execute the crawler run the launch.py command.
```python3 launch.py```

You can restart the crawler from the seed url
(all current progress will be deleted) using the command
```python3 launch.py --restart```

You can specify a different config file to use by using the command with the option
```python3 launch.py --config_file path/to/config```

ARCHITECTURE
-------------------------

### FLOW

The crawler receives a cache host and port from the spacetime servers
and instantiates the config.

It launches a crawler (defined in crawler/\_\_init\_\_.py L5) which creates a 
Frontier and Worker(s) using the optional parameters frontier_factory, and
worker_factory.

When the crawler in started, workers are created that pick up an
undownloaded link from the frontier, download it from our cache server, and
pass the response to your scraper function. The links that are received by
the scraper is added to the list of undownloaded links in the frontier and
the url that was downloaded is marked as complete. The cycle continues until
there are no more urls to be downloaded in the frontier.

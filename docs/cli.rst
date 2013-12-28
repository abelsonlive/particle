
Command Line Interface
=================

``particle`` can be run via a command line interface, here are the args:

.. code-block:: bash

  $ particle --help  
  usage: particle [options]

  Run particle from the command line.

  positional arguments:
    {run,api}

  optional arguments:
    -h, --help  show this help message and exit


.. code-block:: bash

  $ particle run --help
  usage: particle [options] run [-h] [-c CONFIG] [-t TASKS]

  optional arguments:
    -h, --help            show this help message and exit
    -c CONFIG, --config CONFIG
                          The path to your configuration file. 
                          default = particle.yml
    -t TASKS, --tasks TASKS
                          A comma-separated list of tasks to run. 
                          default = twitter,facebook,rssfeeds,promopages

.. code-block:: bash

  $ particle api --help
  usage: particle [options] api [-h] [-p PORT] [-d]

  optional arguments:
    -h, --help            show this help message and exit
    -p PORT, --port PORT  The port on which to serve the API. 
                          default = 3030
    -d, --debug           Whether or not to run the API in debug mode. 
                          default = True


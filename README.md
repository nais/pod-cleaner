# Pod Cleaner

This app will delete pods with containers that kubernetes is unable to create. The most common cause for this is that we've updated the CA-bundle and a container is restarting.

## Development

### Prerequisites

* Python 3.9

### Setup

* Create a virtual environment: `python3 -m venv venv`
* Activate the virtual environment: `source venv/bin/activate`
* Install dependencies: `pip install -r requirements.txt`

### Running tests

* Activate the virtual environment: `source venv/bin/activate`
* Run tests `python -m cleanup_test`

import json

from flask import Flask, request
from waitress import serve

from ..methods import update_cf
from .utils import JSON_UPDATE_SCHEMA
from .utils import validate_json


app = Flask(__name__)

@app.route('/api/update_entries', methods=['POST'])
def update_entries():
    '''Updates existing entries in network configuration files through HTTP requests with JSON data

    Parameters
    ----------
    None

    Raises
    ------
    None

    Returns
    -------
    None or str
    Return 'Content-Type not supported!' if the content type of request is not supported
    '''
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        # Get data from request in Python format
        data = request.json
                
        # Validate data against JSON_UPDATE_SCHEMA
        data_is_valid = validate_json(data, JSON_UPDATE_SCHEMA)
        if not data_is_valid:
            return f'Invalid JSON data format. Please follow the following schema: {JSON_UPDATE_SCHEMA}\n'
        
        # Update config files based on input data
        update_cf(
            app.config['nburl'], 
            app.config['nbtoken'], 
            app.config['cfpath'], 
            data['tenant'], 
            data['ipaddresses']
        )
        return f'IP addresses updated on config file {data["tenant"]}.conf!\n'
        
    else:
        return 'Content-Type not supported!\n'
    

def run_api(nburl, nbtoken, cfpath, port):
    '''Initialize and Run the FLASK/Waitress API server

    Parameters
    ----------
    nburl : str
        Netbox URL,
    nbtoken : str
        Netbox API Token,
    cfpath : str
        Dir path of DNS Masq config files,
    port : int
        HTTP server port,
    
    Raises
    ------
    None

    Returns
    -------
    None
    '''
    app.config['nburl'] = nburl
    app.config['nbtoken'] = nbtoken
    app.config['cfpath'] = cfpath
    # Run Flask in development server mode
    #app.run(debug=True)
    # Run Waitress in production server mode
    serve(app, host="0.0.0.0", port=port)

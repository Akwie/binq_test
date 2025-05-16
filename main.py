from flask import Flask, request, jsonify
from ckanapi import RemoteCKAN
import logging
import json
import os

app = Flask(__name__)

# logging for my own debugging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# env variables
API_TOKEN = os.environ.get("API_TOKEN")
RESOURCE_ID = os.environ.get("RESOURCE_ID")
CKAN_INSTANCE_URL = os.environ.get("CKAN_INSTANCE_URL", "https://www.data.gov.au/data/")

if not API_TOKEN:
    logging.critical("API_TOKEN environment variable must be set.")
    API_TOKEN = "YOUR_API_TOKEN"

# lets make this configurable as most api calls are same with different resource_id default is the business names dataset
# if not can uncomment below and set the resource_id and it will use the business names dataset only also comment line 39

#if not RESOURCE_ID:
#    logging.critical("RESOURCE_ID environment variable must be set.")
#    RESOURCE_ID = "55ad4b1c-5eeb-44ea-8b29-d410da431be3"

@app.route('/search', methods=['POST'])
def search_business_names():
    try:
        body = request.get_json()
        if not body:
            return jsonify({'error': 'Missing JSON payload'}), 400
        
        query = body.get('query')
        filters = body.get('filters', {}) 
        limit = body.get('limit', 5)
        resource_id = body.get('resource_id', '55ad4b1c-5eeb-44ea-8b29-d410da431be3')
        
        if query is None and filters is None:
            return jsonify({'error': 'Missing parameter in JSON payload'}), 400
        

        logging.info(f"Searching with query: {query}, resource_id: {resource_id}, limit: {limit}")
        rc = RemoteCKAN(CKAN_INSTANCE_URL, apikey=API_TOKEN)
        result = rc.action.datastore_search(
            resource_id=resource_id,
            q=query,
            limit=limit,
            filters=filters
        )
        logging.debug(f"CKAN API Response: {json.dumps(result, indent=2)}")  # Log the *entire* response
        return jsonify(result['records']), 200

    except Exception as e:
        error_message = f"Error: {e}"
        logging.exception(error_message)
        return jsonify({'exception': error_message}), 500
    
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

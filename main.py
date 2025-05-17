from flask import Flask, request, jsonify
from ckanapi import RemoteCKAN
import logging
from logging.handlers import RotatingFileHandler # Import for log rotation
import json
import os

app = Flask(__name__)

# Logging setup
log_file = 'app_requests.log'
# set max size of log file to 10MB and keep 5 backup files
file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
# format message to include timestamp, level, message, and line number
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

app.logger.info('Flask application started.')


# env variables
API_TOKEN = os.environ.get("API_TOKEN")
RESOURCE_ID = os.environ.get("RESOURCE_ID") # This is not used if overridden in the request
CKAN_INSTANCE_URL = os.environ.get("CKAN_INSTANCE_URL", "https://www.data.gov.au/data/")

if not API_TOKEN:
    app.logger.critical("API_TOKEN environment variable must be set.") # Use app.logger
    API_TOKEN = "YOUR_API_TOKEN" # Fallback, but ideally this should cause the app to exit or be handled

# Default resource_id if not provided in the request
DEFAULT_RESOURCE_ID = "55ad4b1c-5eeb-44ea-8b29-d410da431be3"

# Log request before sent to api
@app.before_request
def log_request_info():
    """Logs information about the incoming request."""
    app.logger.info(f"Incoming Request: {request.method} {request.url}")
    app.logger.info(f"Request Headers: {request.headers}")
    if request.data:
        try:
            # log request body if it's JSON
            if request.is_json:
                app.logger.info(f"Request JSON Body: {request.get_json()}")
            else:
                # log failures
                app.logger.info(f"Request Body (raw): {request.get_data(as_text=True)}")
        except Exception as e:
            app.logger.warning(f"Could not parse request body: {e}")
            app.logger.info(f"Request Body (raw, on error): {request.data}")


@app.route('/search', methods=['POST'])
def search_business_names():
    try:
        # log end point
        app.logger.info("'/search' endpoint called.")

        body = request.get_json()
        if not body:
            app.logger.warning("Search endpoint: Missing JSON payload.")
            return jsonify({'error': 'Missing JSON payload'}), 400
        
        query = body.get('query')
        filters = body.get('filters', {}) 
        limit = body.get('limit', 5)
        # Use resource_id from request body, or the default if not provided
        resource_id = body.get('resource_id', DEFAULT_RESOURCE_ID)
        
        if query is None and not filters: # Allow search by filters only
            app.logger.warning("Search endpoint: Missing 'query' or 'filters' in JSON payload.")
            return jsonify({'error': "Missing 'query' or 'filters' parameter in JSON payload"}), 400
        
        # Log search parameters
        app.logger.info(f"Searching CKAN with: resource_id='{resource_id}', query='{query}', filters={filters}, limit={limit}")
        
        rc = RemoteCKAN(CKAN_INSTANCE_URL, apikey=API_TOKEN)
        result = rc.action.datastore_search(
            resource_id=resource_id,
            q=query,
            limit=limit,
            filters=filters
        )
        # log response
        app.logger.debug(f"Full CKAN API Response: {json.dumps(result, indent=2)}")
        app.logger.info(f"CKAN search successful. Records found: {len(result.get('records', []))}")
        
        return jsonify(result.get('records', [])), 200

    except Exception as e:
        # Log the exception with stack trace
        app.logger.exception(f"Error in '/search' endpoint: {e}")
        error_message = f"An unexpected error occurred: {str(e)}"
        return jsonify({'exception': error_message}), 500
    
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

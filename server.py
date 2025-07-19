from flask import Flask, request, jsonify
from parrot_agent import create_parrot_agent
from openfloor import Envelope, Payload
import json
import os

app = Flask(__name__)

# Configure CORS for specific origin
@app.after_request
def after_request(response):
    allowed_origin = 'http://127.0.0.1:4000'
    origin = request.headers.get('Origin')
    
    if origin == allowed_origin:
        response.headers.add('Access-Control-Allow-Origin', allowed_origin)
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    
    return response

@app.route('/', methods=['OPTIONS'])
def handle_options():
    """Handle preflight OPTIONS requests"""
    return '', 200

# Create the parrot agent instance
parrot_agent = create_parrot_agent(
    speaker_uri='tag:openfloor-demo.com,2025:parrot-agent',
    service_url=os.environ.get('SERVICE_URL', 'http://localhost:8080/'),
    name='Polly the Parrot',
    organization='OpenFloor Demo Corp',
    description='A friendly parrot that repeats everything you say!'
)

print(f"🦜 Parrot agent created: {parrot_agent.speakerUri}")


@app.route('/', methods=['POST'])
def handle_openfloor_message():
    """Main Open Floor Protocol endpoint"""
    try:
        print(f"🦜 Received request: {json.dumps(request.json, indent=2)}")
        
        # Validate the incoming payload
        if not request.json:
            return jsonify({
                'error': 'Invalid JSON payload'
            }), 400
        
        # Parse the payload
        try:
            if 'openFloor' in request.json:
                # Direct payload format
                payload = Payload.from_dict(request.json)
                incoming_envelope = payload.openFloor
            else:
                # Direct envelope format
                incoming_envelope = Envelope.from_dict(request.json)
        except Exception as parse_error:
            print(f"🦜 Parsing error: {parse_error}")
            return jsonify({
                'error': 'Invalid OpenFloor payload format',
                'details': str(parse_error)
            }), 400
        
        print(f"🦜 Processing envelope from: {incoming_envelope.sender.speakerUri}")
        
        # Process the envelope through the parrot agent
        outgoing_envelope = parrot_agent.process_envelope(incoming_envelope)
        
        # Create response payload
        response_payload = Payload(openFloor=outgoing_envelope)
        response = dict(response_payload)
        
        print(f"🦜 Sending response: {json.dumps(response, indent=2, default=str)}")
        
        return jsonify(response)
        
    except Exception as error:
        print(f"🦜 Error processing request: {error}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(error)
        }), 500
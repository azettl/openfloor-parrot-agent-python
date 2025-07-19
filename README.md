
# Building an Open Floor Parrot Agent in Python

In this short guide, we will build a simple parrot agent together using Python. The parrot agent will simply repeat everything you send him and a small 🦜 emoji in front of the return. We will create the [Open Floor Protocol](https://github.com/open-voice-interoperability/openfloor-docs)-compliant agent with the help of the [openfloor](https://test.pypi.org/project/openfloor/) Python package.

## Initial Setup

First, let's set up our project by creating the project folder and installing the required packages:

```bash
mkdir parrot-agent
cd parrot-agent
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Create a `requirements.txt` file with the following content:

```txt
--extra-index-url https://test.pypi.org/simple/
events==0.5
jsonpath-ng>=1.5.0
openfloor
flask
```

Then install the dependencies:

```bash
pip install -r requirements.txt
```

Now that the basic setup is done, let us start coding together!

## Step 1: Building the Parrot Agent Class

Let's create our main agent file. Create a new file `parrot_agent.py`, this will contain the main logic of our agent.

### Step 1.1: Add the imports

Let's start with importing everything we need from the `openfloor` package, add them at the top of your `parrot_agent.py` file:

```python
from openfloor import (
    BotAgent,
    Manifest,
    Identification,
    Capability,
    SupportedLayers,
    UtteranceEvent,
    Envelope,
    DialogEvent,
    TextFeature,
    To,
    Sender,
    PublishManifestsEvent,
    Parameters
)
```

**Why these imports?**
-   `BotAgent` - The base class we'll extend
-   `Manifest` - To define our agent's capabilities and identification
-   `UtteranceEvent` - The type of event we'll handle for text messages
-   `Envelope` - Container for Open Floor messages
-   `DialogEvent` and `TextFeature` - To create text responses
-   `To` and `Sender` - For message addressing

### Step 1.2: Start the ParrotAgent class

Now let's start creating our `ParrotAgent` class by extending the `BotAgent`:

```python
class ParrotAgent(BotAgent):
    """
    ParrotAgent - A simple agent that echoes back whatever it receives
    Extends BotAgent to provide parrot functionality
    """
    
    def __init__(self, manifest: Manifest):
        super().__init__(manifest)
        print(f"🦜 Parrot Agent initialized with speaker URI: {self.speakerUri}")
```

**What we just did:**
-   Created a class that extends `BotAgent`
-   Added a constructor that takes a manifest and passes it to the parent class
-   The manifest will define what our agent can do

### Step 1.3: Override the utterance handler

The `BotAgent` class provides a default `bot_on_utterance` method that we need to override. This is where the magic happens:

```python
    def bot_on_utterance(self, event: UtteranceEvent, in_envelope: Envelope, out_envelope: Envelope) -> None:
        """
        Override the utterance handler to provide parrot functionality
        """
        print("🦜 Processing utterance event")
        
        try:
            # Extract the dialog event from the utterance parameters
            dialog_event_data = event.parameters.get("dialogEvent")
            if not dialog_event_data:
                self._send_error_response("*chirp* I didn't receive a valid dialog event!", out_envelope)
                return
            
            # Convert to DialogEvent object if it's a dictionary
            if isinstance(dialog_event_data, dict):
                dialog_event = DialogEvent.from_dict(dialog_event_data)
            elif isinstance(dialog_event_data, DialogEvent):
                dialog_event = dialog_event_data
            else:
                self._send_error_response("*chirp* I didn't receive a valid dialog event!", out_envelope)
                return
            
            # Check if there's a text feature
            text_feature = dialog_event.features.get("text")
            if not text_feature or not hasattr(text_feature, 'tokens') or not text_feature.tokens:
                self._send_error_response("*chirp* I can only repeat text messages!", out_envelope)
                return
            
            # Extract the original text from tokens
            original_text = "".join(token.value for token in text_feature.tokens if token.value)
            
            # Create parrot response with emoji prefix
            parrot_text = f"🦜 {original_text}"
            
            # Create the response dialog event
            response_dialog = DialogEvent(
                speakerUri=self.speakerUri,
                features={"text": TextFeature(values=[parrot_text])}
            )
            
            # Create and add the utterance event to the response
            response_utterance = UtteranceEvent(
                dialogEvent=response_dialog,
                to=To(speakerUri=in_envelope.sender.speakerUri)
            )
            
            out_envelope.events.append(response_utterance)
            print(f"🦜 Echoing back: {parrot_text}")
            
        except Exception as error:
            print(f"🦜 Error in parrot utterance handling: {error}")
            self._send_error_response("*confused chirp* Something went wrong while trying to repeat that!", out_envelope)
```

**The parroting logic:**
-   Extract the dialog event from the utterance parameters
-   Get the text feature and extract text from tokens
-   Add the 🦜 emoji prefix
-   Create a dialog event response
-   Send it back to the original sender

### Step 1.4: Add helper methods

Let's add the helper methods we called in `bot_on_utterance`:

```python
    def _send_error_response(self, message: str, out_envelope: Envelope) -> None:
        """Helper method to send error responses"""
        error_dialog = DialogEvent(
            speakerUri=self.speakerUri,
            features={"text": TextFeature(values=[message])}
        )
        
        error_utterance = UtteranceEvent(
            dialogEvent=error_dialog
        )
        
        out_envelope.events.append(error_utterance)
```

### Step 1.5: Override the manifest handler

We also need to handle manifest requests properly:

```python
    def bot_on_get_manifests(self, event, in_envelope: Envelope, out_envelope: Envelope) -> None:
        """
        Handle manifest requests by sending our capabilities
        """
        print("🦜 Sending manifest information")
        
        # Create the publish manifests response
        publish_event = PublishManifestsEvent(
            parameters=Parameters({
                "servicingManifests": [self._manifest],
                "discoveryManifests": []
            }),
            to=To(speakerUri=in_envelope.sender.speakerUri)
        )
        
        out_envelope.events.append(publish_event)
```

### Step 1.6: Add the factory function

After the class, add this factory function with the default configuration:

```python
def create_parrot_agent(
    speaker_uri: str,
    service_url: str,
    name: str = "Parrot Agent",
    organization: str = "OpenFloor Demo",
    description: str = "A simple parrot agent that echoes back messages with a 🦜 emoji"
) -> ParrotAgent:
    """
    Factory function to create a ParrotAgent with default configuration
    """
    
    # Create the identification
    identification = Identification(
        speakerUri=speaker_uri,
        serviceUrl=service_url,
        organization=organization,
        conversationalName=name,
        synopsis=description
    )
    
    # Create the capabilities
    capability = Capability(
        keyphrases=['echo', 'repeat', 'parrot', 'say'],
        descriptions=[
            'Echoes back any text message with a 🦜 emoji',
            'Repeats user input verbatim',
            'Simple text mirroring functionality'
        ],
        supportedLayers=SupportedLayers(
            input=["text"],
            output=["text"]
        )
    )
    
    # Create the manifest
    manifest = Manifest(
        identification=identification,
        capabilities=[capability]
    )
    
    return ParrotAgent(manifest)
```

**What this factory does:**
-   Takes configuration options with some defaults
-   Creates an identification object that describes our agent
-   Defines capabilities that tell others what our agent can do
-   Creates a manifest that combines identification and capabilities
-   Returns a new ParrotAgent instance

## Step 2: Building the Flask Server

The agent itself is done, but how to talk to it? We need to build our Flask server for this, so start with creating a `server.py` file.

### Step 2.1: Add imports

Add these imports at the top:

```python
from flask import Flask, request, jsonify
from parrot_agent import create_parrot_agent
from openfloor import Envelope, Payload
import json
import os
```

### Step 2.2: Create the Flask app

```python
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
```

**Why this CORS setup?**
-   Only allows requests from the specific domain
-   Handles preflight `OPTIONS` requests
-   Restricts to `POST` methods and the `Content-Type` header

### Step 2.3: Create the agent instance

Now we need to create our parrot by using the factory function `create_parrot_agent`.

```python
# Create the parrot agent instance
parrot_agent = create_parrot_agent(
    speaker_uri='tag:openfloor-demo.com,2025:parrot-agent',
    service_url=os.environ.get('SERVICE_URL', 'http://localhost:8080/'),
    name='Polly the Parrot',
    organization='OpenFloor Demo Corp',
    description='A friendly parrot that repeats everything you say!'
)

print(f"🦜 Parrot agent created: {parrot_agent.speakerUri}")
```

### Step 2.4: Build the main endpoint step by step

Now we have the agent and the Flask app, but the most important part is still missing, and that's our endpoint:

```python
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
```

**What's happening here:**
-   Validate that we received valid JSON
-   Parse the payload into an Open Floor envelope
-   Process it through our parrot agent
-   Create and send the response as a properly formatted payload

## Step 3: Creating the Entry Point

We end by creating a simple `main.py` as our entry point:

```python
from server import app
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🦜 Parrot Agent server starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
```

## Step 4: Final Setup

Your project structure should now look like this:

```
parrot-agent/
├── requirements.txt
├── parrot_agent.py
├── server.py
└── main.py
```

## Test Your Implementation

Run this to test:

```bash
python main.py
```

Send your manifest or utterance requests to `http://localhost:8080/` to see if it's working! You can also download the simple single HTML file manifest and utterance chat [azettl/openfloor-js-chat](https://github.com/azettl/openfloor-js-chat) to test your agent locally.

If you found this guide useful, follow me for more and let me know what you build with it in the comments!
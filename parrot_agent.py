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

class ParrotAgent(BotAgent):
    """
    ParrotAgent - A simple agent that echoes back whatever it receives
    Extends BotAgent to provide parrot functionality
    """
    
    def __init__(self, manifest: Manifest):
        super().__init__(manifest)
        print(f"🦜 Parrot Agent initialized with speaker URI: {self.speakerUri}")

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
from fastapi import APIRouter
from google.cloud import texttospeech

router = APIRouter()

@router.get("/tts")
async def get_voice(text: str, mood: str = "lazy"):
    try:
        client = texttospeech.TextToSpeechClient()
        
        pitch = "+5st" if mood == "angry" else "-2st"
        rate = "fast" if mood == "angry" else "slow"
        
        ssml_text = f"""
        <speak>
            <prosody pitch='{pitch}' rate='{rate}'>{text}</prosody>
        </speak>
        """
        
        synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="ko-KR", 
            name="ko-KR-Wavenet-A"
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        
        response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
        
        return {"audio_length": len(response.audio_content)}
    except Exception as e:
        return {"error": f"TTS generation failed: {str(e)}"}

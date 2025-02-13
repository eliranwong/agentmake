from agentmake.utils.manage_package import installPipPackage
REQUIREMENTS = ["pydub", "SpeechRecognition"]
try:
    import speech_recognition as sr
    from pydub import AudioSegment
except:
    for i in REQUIREMENTS:
        installPipPackage(i)
    import speech_recognition as sr
    from pydub import AudioSegment

from agentmake.utils.tts_languages import googleSpeeckToTextLanguages

def transcribe_audio_google(audio_filepath: str, language: str, **kwargs):

    import speech_recognition as sr
    from pydub import AudioSegment

    from agentmake import PACKAGE_PATH
    import os, io

    llmInterface = "google_alternative"

    if audio_filepath and os.path.isfile(audio_filepath):
        if llmInterface in ("vertexai", "genai"):

            # create a speech recognition object
            r = sr.Recognizer()

            # convert mp3
            if audio_filepath.lower().endswith(".mp3"):
                sound = AudioSegment.from_mp3(audio_filepath)
                audio_filepath = os.path.join(PACKAGE_PATH, "temp", os.path.basename(audio_filepath)[:-4]+".wav")
                sound.export(audio_filepath, format='wav')

            # open the audio file
            with sr.AudioFile(audio_filepath) as source:
                # listen for the data (load audio to memory)
                audio_data = r.record(source)

            # recognize (convert from speech to text)
            try:
                transcription = r.recognize_google(audio_data, language=language)
                print("```transcription")
                print(transcription)
                print("```")
            except sr.UnknownValueError:
                print("Speech recognition could not understand the audio")
            except sr.RequestError as e:
                print("Could not request results from Google Web Speech API; {0}".format(e))

            return ""

        elif llmInterface == "google_alternative":
            #https://cloud.google.com/speech-to-text/docs/sync-recognize#speech-sync-recognize-python

            # not supported on Android; so import here
            from google.cloud import speech

            # convert mp3
            if audio_filepath.lower().endswith(".mp3"):
                sound = AudioSegment.from_mp3(audio_filepath)
                audio_filepath = os.path.join(PACKAGE_PATH, "temp", os.path.basename(audio_filepath)[:-4]+".wav")
                sound.export(audio_filepath, format='wav')

            # Instantiates a client
            client = speech.SpeechClient.from_service_account_json(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
            #client = speech.SpeechClient()

            # Loads the audio into memory
            with io.open(audio_filepath, 'rb') as audio_filepath:
                content = audio_filepath.read()

            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                #encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                #sample_rate_hertz=16000,
                language_code=language,
            )

            # Performs speech recognition on the audio file
            response = client.recognize(
                config=config,
                audio=audio,
            )

            # Print the transcription
            for result in response.results:
                transcript = f"The transcript of the audio is: {result.alternatives[0].transcript}"
                return transcript
            
            return ""

    return None

TOOL_SCHEMA = {
    "name": "transcribe_audio_google",
    "description": '''Transcribe audio into text with Google''',
    "parameters": {
        "type": "object",
        "properties": {
            "audio_filepath": {
                "type": "string",
                "description": "Return the audio file path that I specified in my requests. Return an empty string '' if it is not specified.",
            },
            "language": {
                "type": "string",
                "description": "Audio language",
                "enum": list(googleSpeeckToTextLanguages.values()),
            },
        },
        "required": ["audio_filepath", "language"],
    },
}

TOOL_FUNCTION = transcribe_audio_google
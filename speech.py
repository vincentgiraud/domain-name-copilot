"""Optional text-to-speech via Azure Cognitive Services."""
from __future__ import annotations

import logging

from config import get_settings

logger = logging.getLogger(__name__)


def text_to_speech(text: str) -> None:
    """Speak `text` through the default speaker. No-op if speech is unconfigured."""
    settings = get_settings()
    if not (settings.azure_speech_key and settings.azure_speech_region):
        logger.warning("Speech not configured; skipping TTS for %r", text)
        return

    import azure.cognitiveservices.speech as speechsdk

    speech_config = speechsdk.SpeechConfig(
        subscription=settings.azure_speech_key, region=settings.azure_speech_region
    )
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config
    )
    result = synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        logger.info("Speech synthesized for text [%s]", text)
    elif result.reason == speechsdk.ResultReason.Canceled:
        details = result.cancellation_details
        logger.error("Speech synthesis canceled: %s", details.reason)
        if details.reason == speechsdk.CancellationReason.Error:
            logger.error("Error details: %s", details.error_details)

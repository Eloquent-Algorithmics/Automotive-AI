# test_audio_output.py

from unittest.mock import MagicMock, patch
import azure.cognitiveservices.speech as speechsdk

# Replace this with the correct import path for your functions
from automotive_ai._audio._audio_output import tts_output, ssml_output


def test_tts_output_success(monkeypatch):
    # Set up environment variables
    monkeypatch.setenv("AZURE_SPEECH_REGION", "test_region")
    monkeypatch.setenv("AZURE_SPEECH_KEY", "test_key")
    monkeypatch.setenv("AZURE_SPEECH_VOICE", "test_voice")

    response_text = "Hello, this is a test."

    # Mock the required classes and methods
    with patch("automotive_ai._audio._audio_output.speechsdk.SpeechConfig"), patch(
        "automotive_ai._audio._audio_output.speechsdk.SpeechSynthesizer"
    ) as MockSpeechSynthesizer:

        # Set up the mock result
        mock_result = MagicMock()
        mock_result.reason = speechsdk.ResultReason.SynthesizingAudioCompleted

        # Configure the mock to return the mock result
        mock_synthesizer_instance = MockSpeechSynthesizer.return_value
        mock_synthesizer_instance.speak_text_async.return_value.get.return_value = (
            mock_result
        )

        # Call the function
        tts_output(response_text)

        # Assertions
        mock_synthesizer_instance.speak_text_async.assert_called_once_with(
            response_text
        )


def test_tts_output_canceled(monkeypatch, capsys):
    # Set up environment variables
    monkeypatch.setenv("AZURE_SPEECH_REGION", "test_region")
    monkeypatch.setenv("AZURE_SPEECH_KEY", "test_key")
    monkeypatch.setenv("AZURE_SPEECH_VOICE", "test_voice")

    response_text = "Hello, this is a test."

    # Mock the required classes and methods
    with patch("automotive_ai._audio._audio_output.speechsdk.SpeechConfig"), patch(
        "automotive_ai._audio._audio_output.speechsdk.SpeechSynthesizer"
    ) as MockSpeechSynthesizer:

        # Set up the mock result and cancellation details
        mock_result = MagicMock()
        mock_result.reason = speechsdk.ResultReason.Canceled
        mock_cancellation_details = MagicMock()
        mock_cancellation_details.reason = speechsdk.CancellationReason.Error
        mock_cancellation_details.error_details = "Mock error details"
        mock_result.cancellation_details = mock_cancellation_details

        # Configure the mock to return the mock result
        mock_synthesizer_instance = MockSpeechSynthesizer.return_value
        mock_synthesizer_instance.speak_text_async.return_value.get.return_value = (
            mock_result
        )

        # Call the function
        tts_output(response_text)

        # Capture printed output
        captured = capsys.readouterr()
        assert "Speech synthesis canceled" in captured.out
        assert "Error details: Mock error details" in captured.out


def test_ssml_output_success(monkeypatch):
    # Set up environment variables
    monkeypatch.setenv("AZURE_SPEECH_REGION", "test_region")
    monkeypatch.setenv("AZURE_SPEECH_KEY", "test_key")
    monkeypatch.setenv("AZURE_SPEECH_VOICE", "test_voice")

    response_text = "<speak>This is SSML text.</speak>"

    # Mock the required classes and methods
    with patch("automotive_ai._audio._audio_output.speechsdk.SpeechConfig"), patch(
        "automotive_ai._audio._audio_output.speechsdk.SpeechSynthesizer"
    ) as MockSpeechSynthesizer:

        # Set up the mock result
        mock_result = MagicMock()
        mock_result.reason = speechsdk.ResultReason.SynthesizingAudioCompleted

        # Configure the mock to return the mock result
        mock_synthesizer_instance = MockSpeechSynthesizer.return_value
        mock_synthesizer_instance.speak_ssml_async.return_value.get.return_value = (
            mock_result
        )

        # Call the function
        ssml_output(response_text)

        # Assertions
        mock_synthesizer_instance.speak_ssml_async.assert_called_once_with(
            response_text
        )


def test_ssml_output_canceled(monkeypatch, capsys):
    # Set up environment variables
    monkeypatch.setenv("AZURE_SPEECH_REGION", "test_region")
    monkeypatch.setenv("AZURE_SPEECH_KEY", "test_key")
    monkeypatch.setenv("AZURE_SPEECH_VOICE", "test_voice")

    response_text = "<speak>This is SSML text.</speak>"

    # Mock the required classes and methods
    with patch("automotive_ai._audio._audio_output.speechsdk.SpeechConfig"), patch(
        "automotive_ai._audio._audio_output.speechsdk.SpeechSynthesizer"
    ) as MockSpeechSynthesizer:

        # Set up the mock result and cancellation details
        mock_result = MagicMock()
        mock_result.reason = speechsdk.ResultReason.Canceled
        mock_cancellation_details = MagicMock()
        mock_cancellation_details.reason = speechsdk.CancellationReason.Error
        mock_cancellation_details.error_details = "Mock error details"
        mock_result.cancellation_details = mock_cancellation_details

        # Configure the mock to return the mock result
        mock_synthesizer_instance = MockSpeechSynthesizer.return_value
        mock_synthesizer_instance.speak_ssml_async.return_value.get.return_value = (
            mock_result
        )

        # Call the function
        ssml_output(response_text)

        # Capture printed output
        captured = capsys.readouterr()
        assert "Speech synthesis canceled" in captured.out
        assert "Error details: Mock error details" in captured.out

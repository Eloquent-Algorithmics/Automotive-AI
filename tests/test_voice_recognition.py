import unittest
from unittest.mock import patch, MagicMock
from automotive_ai._voice._voice_recognition import (
    get_similarity_score,
    recognize_command,
    recognize_speech,
)
import speech_recognition as sr


class TestVoiceRecognition(unittest.TestCase):
    def test_get_similarity_score_identical_texts(self):
        text1 = "Turn on the headlights"
        text2 = "Turn on the headlights"
        score = get_similarity_score(text1, text2)
        self.assertGreaterEqual(score, 0.99)

    def test_get_similarity_score_different_texts(self):
        text1 = "Turn on the headlights"
        text2 = "Open the sunroof"
        score = get_similarity_score(text1, text2)
        self.assertLessEqual(score, 0.7)

    def test_get_similarity_score_symmetry(self):
        text1 = "Increase the volume"
        text2 = "Raise the sound level"
        score1 = get_similarity_score(text1, text2)
        score2 = get_similarity_score(text2, text1)
        self.assertAlmostEqual(score1, score2, places=5)

    @patch("automotive_ai_voice_voice_recognition.nlp")
    def test_recognize_command_exact_match(self, mock_nlp):
        text = "Open the sunroof"
        commands = ["Turn on the headlights", "Open the sunroof", "Play music"]

        # Mock the similarity scores
        mock_doc = MagicMock()
        mock_doc.similarity.side_effect = lambda other: (
            1.0 if other.text == text else 0.0
        )
        mock_nlp.return_value = mock_doc

        result = recognize_command(text, commands)
        self.assertEqual(result, "Open the sunroof")

    @patch("automotive_ai_voice_voice_recognition.get_similarity_score")
    def test_recognize_command_no_match(self, mock_get_similarity_score):
        text = "Turn off the radio"
        commands = ["Turn on the headlights", "Open the sunroof", "Play music"]

        # Simulate low similarity for all commands
        mock_get_similarity_score.return_value = 0.5  # Below the threshold of 0.7

        result = recognize_command(text, commands)
        self.assertIsNone(result)

    @patch("automotive_ai_voice_voice_recognition.get_similarity_score")
    def test_recognize_command_best_match(self, mock_get_similarity_score):
        text = "Start the music"
        commands = ["Turn on the headlights", "Open the sunroof", "Play music"]

        # Simulate similarity scores
        def side_effect(input_text, command):
            if command == "Play music":
                return 0.85  # Above threshold
            else:
                return 0.6  # Below threshold

        mock_get_similarity_score.side_effect = side_effect

        result = recognize_command(text, commands)
        self.assertEqual(result, "Play music")

    @patch("automotive_ai_voice_voice_recognition.sr.Recognizer")
    def test_recognize_speech_success(self, mock_recognizer_class):
        # Mock the recognizer instance
        mock_recognizer_instance = MagicMock()
        mock_recognizer_class.return_value = mock_recognizer_instance

        # Mock the listen method
        mock_recognizer_instance.listen.return_value = "audio_data"

        # Mock the recognize_azure method
        mock_recognizer_instance.recognize_azure.return_value = (
            "Turn on the headlights",
            None,
        )

        # Mock the Microphone
        with patch("automotive_ai_voice_voice_recognition.sr.Microphone"):
            result = recognize_speech()
            self.assertEqual(result, "Turn on the headlights")

    @patch("automotive_ai_voice_voice_recognition.sr.Recognizer")
    def test_recognize_speech_timeout(self, mock_recognizer_class):
        # Mock the recognizer instance
        mock_recognizer_instance = MagicMock()
        mock_recognizer_class.return_value = mock_recognizer_instance

        # Simulate a timeout error
        mock_recognizer_instance.listen.side_effect = sr.WaitTimeoutError()

        # Mock the Microphone
        with patch("automotive_ai_voice_voice_recognition.sr.Microphone"):
            result = recognize_speech()
            self.assertIsNone(result)

    @patch("automotive_ai_voice_voice_recognition.sr.Recognizer")
    def test_recognize_speech_unknown_value_error(self, mock_recognizer_class):
        # Mock the recognizer instance
        mock_recognizer_instance = MagicMock()
        mock_recognizer_class.return_value = mock_recognizer_instance

        mock_recognizer_instance.listen.return_value = "audio_data"
        mock_recognizer_instance.recognize_azure.side_effect = sr.UnknownValueError()

        # Mock the Microphone
        with patch("automotive_ai_voice_voice_recognition.sr.Microphone"):
            result = recognize_speech()
            self.assertIsNone(result)

    @patch("automotive_ai_voice_voice_recognition.sr.Recognizer")
    def test_recognize_speech_request_error(self, mock_recognizer_class):
        # Mock the recognizer instance
        mock_recognizer_instance = MagicMock()
        mock_recognizer_class.return_value = mock_recognizer_instance

        mock_recognizer_instance.listen.return_value = "audio_data"
        mock_recognizer_instance.recognize_azure.side_effect = sr.RequestError(
            "API unavailable"
        )

        # Mock the Microphone
        with patch("automotive_ai_voice_voice_recognition.sr.Microphone"):
            result = recognize_speech()
            self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()

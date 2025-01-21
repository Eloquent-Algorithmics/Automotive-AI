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
        text1 = "What is the engine rpm"
        text2 = "How fast is the engine spinning"
        score = get_similarity_score(text1, text2)
        self.assertGreaterEqual(score, 0.85)

    def test_get_similarity_score_different_texts(self):
        text1 = "read trouble codes"
        text2 = "are there any current dtcs"
        score = get_similarity_score(text1, text2)
        self.assertLessEqual(score, 0.7)

    def test_get_similarity_score_symmetry(self):
        text1 = "Send me a diagnostic report"
        text2 = "What is going on with this vehicle"
        score1 = get_similarity_score(text1, text2)
        score2 = get_similarity_score(text2, text1)
        self.assertAlmostEqual(score1, score2, places=5)

    @patch("automotive_ai._voice._voice_recognition.nlp")
    def test_recognize_command_exact_match(self, mock_nlp):
        text = "engine rpm"
        commands = ["engine rpm", "read trouble codes", "send a diagnostic report"]

        # Mock the similarity scores
        mock_doc = MagicMock()
        mock_doc.similarity.side_effect = lambda other: (
            1.0 if other.text == text else 0.0
        )
        mock_nlp.return_value = mock_doc

        result = recognize_command(text, commands)
        self.assertEqual(result, "engine rpm")

    @patch("automotive_ai._voice._voice_recognition.get_similarity_score")
    def test_recognize_command_no_match(self, mock_get_similarity_score):
        text = "read trouble codes"
        commands = ["engine rpm", "read trouble codes", "send a diagnostic report"]

        # Simulate low similarity for all commands
        mock_get_similarity_score.return_value = 0.5  # Below the threshold of 0.7

        result = recognize_command(text, commands)
        self.assertIsNone(result, "read trouble codes")

    @patch("automotive_ai._voice._voice_recognition.get_similarity_score")
    def test_recognize_command_best_match(self, mock_get_similarity_score):
        text = "Send a diagnostic report"
        commands = ["engine rpm", "read trouble codes", "send a diagnostic report"]

        # Simulate similarity scores
        def side_effect(input_text, command):
            if command == "send a diagnostic report":
                return 0.85  # Above threshold
            else:
                return 0.6  # Below threshold

        mock_get_similarity_score.side_effect = side_effect

        result = recognize_command(text, commands)
        self.assertEqual(result, "send a diagnostic report")

    @patch("automotive_ai._voice._voice_recognition.sr.Recognizer")
    def test_recognize_speech_success(self, mock_recognizer_class):
        # Mock the recognizer instance
        mock_recognizer_instance = MagicMock()
        mock_recognizer_class.return_value = mock_recognizer_instance

        # Mock the listen method
        mock_recognizer_instance.listen.return_value = "audio_data"

        # Mock the recognize_azure method
        mock_recognizer_instance.recognize_azure.return_value = (
            "What is the engine rpm",
            None,
        )

        # Mock the Microphone
        with patch("automotive_ai._voice._voice_recognition.sr.Microphone"):
            result = recognize_speech()
            self.assertEqual(result, "engine rpm")

    @patch("automotive_ai._voice._voice_recognition.sr.Recognizer")
    def test_recognize_speech_timeout(self, mock_recognizer_class):
        # Mock the recognizer instance
        mock_recognizer_instance = MagicMock()
        mock_recognizer_class.return_value = mock_recognizer_instance

        # Simulate a timeout error
        mock_recognizer_instance.listen.side_effect = sr.WaitTimeoutError()

        # Mock the Microphone
        with patch("automotive_ai._voice._voice_recognition.sr.Microphone"):
            result = recognize_speech()
            self.assertIsNone(result)

    @patch("automotive_ai._voice._voice_recognition.sr.Recognizer")
    def test_recognize_speech_unknown_value_error(self, mock_recognizer_class):
        # Mock the recognizer instance
        mock_recognizer_instance = MagicMock()
        mock_recognizer_class.return_value = mock_recognizer_instance

        mock_recognizer_instance.listen.return_value = "audio_data"
        mock_recognizer_instance.recognize_azure.side_effect = sr.UnknownValueError()

        # Mock the Microphone
        with patch("automotive_ai._voice._voice_recognition.sr.Microphone"):
            result = recognize_speech()
            self.assertIsNone(result)

    @patch("automotive_ai._voice._voice_recognition.sr.Recognizer")
    def test_recognize_speech_request_error(self, mock_recognizer_class):
        # Mock the recognizer instance
        mock_recognizer_instance = MagicMock()
        mock_recognizer_class.return_value = mock_recognizer_instance

        mock_recognizer_instance.listen.return_value = "audio_data"
        mock_recognizer_instance.recognize_azure.side_effect = sr.RequestError(
            "API unavailable"
        )

        # Mock the Microphone
        with patch("automotive_ai._voice._voice_recognition.sr.Microphone"):
            result = recognize_speech()
            self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()

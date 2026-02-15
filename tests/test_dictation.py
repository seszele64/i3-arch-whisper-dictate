"""Tests for dictation workflow integration."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from whisper_dictate.dictation import DictationService


class TestDictationService:
    """Test the DictationService class."""
    
    def test_init(self, mock_config):
        """Test DictationService initialization."""
        service = DictationService(mock_config)
        
        assert service.config == mock_config
        assert service.audio_recorder is not None
        assert service.transcriber is not None
        assert service.clipboard is not None
    
    def test_dictate_success(self, mock_config, mock_transcription_result):
        """Test successful dictation workflow."""
        service = DictationService(mock_config)
        
        with patch.object(service.audio_recorder, 'record_to_file') as mock_record, \
             patch.object(service.transcriber, 'transcribe_audio') as mock_transcribe, \
             patch.object(service.clipboard, 'copy_to_clipboard') as mock_copy:
            
            # Mock successful operations
            mock_record.return_value = Path("/tmp/test.wav")
            mock_transcribe.return_value = mock_transcription_result
            mock_copy.return_value = True
            
            result = service.dictate()
            
            assert result is not None
            assert result.text == "This is a test transcription."
            assert result.language == "en"
            
            mock_record.assert_called_once()
            mock_transcribe.assert_called_once_with(Path("/tmp/test.wav"))
            mock_copy.assert_called_once_with("This is a test transcription.")
    
    def test_dictate_without_clipboard_copy(self, mock_config, mock_transcription_result):
        """Test dictation without clipboard copying."""
        mock_config.copy_to_clipboard = False
        service = DictationService(mock_config)
        
        with patch.object(service.audio_recorder, 'record_to_file') as mock_record, \
             patch.object(service.transcriber, 'transcribe_audio') as mock_transcribe, \
             patch.object(service.clipboard, 'copy_to_clipboard') as mock_copy:
            
            mock_record.return_value = Path("/tmp/test.wav")
            mock_transcribe.return_value = mock_transcription_result
            
            result = service.dictate()
            
            assert result is not None
            assert result.text == "This is a test transcription."
            mock_copy.assert_not_called()
    
    def test_dictate_with_custom_duration(self, mock_config, mock_transcription_result):
        """Test dictation with custom duration."""
        service = DictationService(mock_config)
        
        with patch.object(service.audio_recorder, 'record_to_file') as mock_record, \
             patch.object(service.transcriber, 'transcribe_audio') as mock_transcribe, \
             patch.object(service.clipboard, 'copy_to_clipboard') as mock_copy:
            
            mock_record.return_value = Path("/tmp/test.wav")
            mock_transcribe.return_value = mock_transcription_result
            mock_copy.return_value = True
            
            result = service.dictate(duration=10.0)
            
            assert result is not None
            mock_record.assert_called_once_with(10.0)
    
    def test_dictate_recording_failure(self, mock_config):
        """Test handling of recording failures."""
        service = DictationService(mock_config)
        
        with patch.object(service.audio_recorder, 'record_to_file') as mock_record:
            mock_record.side_effect = Exception("Recording failed")
            
            with pytest.raises(Exception, match="Recording failed"):
                service.dictate()
    
    def test_dictate_transcription_failure(self, mock_config):
        """Test handling of transcription failures."""
        service = DictationService(mock_config)
        
        with patch.object(service.audio_recorder, 'record_to_file') as mock_record, \
             patch.object(service.transcriber, 'transcribe_audio') as mock_transcribe:
            
            mock_record.return_value = Path("/tmp/test.wav")
            mock_transcribe.side_effect = Exception("Transcription failed")
            
            with pytest.raises(Exception, match="Transcription failed"):
                service.dictate()
    
    def test_dictate_clipboard_failure(self, mock_config, mock_transcription_result):
        """Test handling of clipboard failures (should not fail dictation)."""
        service = DictationService(mock_config)
        
        with patch.object(service.audio_recorder, 'record_to_file') as mock_record, \
             patch.object(service.transcriber, 'transcribe_audio') as mock_transcribe, \
             patch.object(service.clipboard, 'copy_to_clipboard') as mock_copy, \
             patch('os.unlink') as mock_unlink:
            
            mock_record.return_value = Path("/tmp/test.wav")
            mock_transcribe.return_value = mock_transcription_result
            mock_copy.return_value = False  # Clipboard copy fails
            mock_unlink.return_value = None
            
            result = service.dictate()
            
            assert result is not None
            assert result.text == "This is a test transcription."
            mock_copy.assert_called_once()
    
    def test_dictate_file_cleanup_on_success(self, mock_config, mock_transcription_result):
        """Test that temporary files are cleaned up on success."""
        service = DictationService(mock_config)
        
        temp_file = Path("/tmp/test.wav")
        mock_path = MagicMock(spec=Path)
        mock_path.__str__.return_value = str(temp_file)
        mock_path.exists.return_value = True
        
        with patch.object(service.audio_recorder, 'record_to_file') as mock_record, \
             patch.object(service.transcriber, 'transcribe_audio') as mock_transcribe, \
             patch.object(service.clipboard, 'copy_to_clipboard') as mock_copy:
            
            mock_record.return_value = mock_path
            mock_transcribe.return_value = mock_transcription_result
            mock_copy.return_value = True
            
            result = service.dictate()
            
            assert result is not None
            mock_path.unlink.assert_called_once()
    
    def test_dictate_file_cleanup_on_failure(self, mock_config):
        """Test that temporary files are cleaned up even on failure."""
        service = DictationService(mock_config)
        
        temp_file = Path("/tmp/test.wav")
        mock_path = MagicMock(spec=Path)
        mock_path.__str__.return_value = str(temp_file)
        mock_path.exists.return_value = True
        
        with patch.object(service.audio_recorder, 'record_to_file') as mock_record, \
             patch.object(service.transcriber, 'transcribe_audio') as mock_transcribe:
            
            mock_record.return_value = mock_path
            mock_transcribe.side_effect = Exception("Transcription failed")
            
            with pytest.raises(Exception):
                service.dictate()
            
            mock_path.unlink.assert_called_once()
    
    def test_dictate_file_cleanup_nonexistent_file(self, mock_config, mock_transcription_result):
        """Test cleanup when file doesn't exist."""
        service = DictationService(mock_config)
        
        temp_file = Path("/tmp/nonexistent.wav")
        mock_path = MagicMock(spec=Path)
        mock_path.__str__.return_value = str(temp_file)
        mock_path.exists.return_value = True
        mock_path.unlink.side_effect = OSError("File not found")
        
        with patch.object(service.audio_recorder, 'record_to_file') as mock_record, \
             patch.object(service.transcriber, 'transcribe_audio') as mock_transcribe, \
             patch.object(service.clipboard, 'copy_to_clipboard') as mock_copy:
            
            mock_record.return_value = mock_path
            mock_transcribe.return_value = mock_transcription_result
            mock_copy.return_value = True
            
            result = service.dictate()
            
            assert result is not None
            mock_path.unlink.assert_called_once()
    
    def test_get_system_info(self, mock_config):
        """Test system information gathering."""
        service = DictationService(mock_config)
        
        with patch.object(service.audio_recorder, 'get_audio_devices') as mock_devices, \
             patch.object(service.clipboard, 'available_tools', new_callable=lambda: ["xclip", "xsel"]):
            
            mock_devices.return_value = ("default", "pulse")
            
            info = service.get_system_info()
            
            assert "audio_devices" in info
            assert "clipboard_tools" in info
            assert "config" in info
            
            assert info["audio_devices"] == ("default", "pulse")
            assert info["clipboard_tools"] == ["xclip", "xsel"]
            assert info["config"]["audio_sample_rate"] == 16000
            assert info["config"]["copy_to_clipboard"] is True
            assert info["config"]["openai_model"] == "whisper-1"
rumen / test_config / test_delete_setting.py
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import ConfigManager


def test_delete_input_files_setting():
    """Test that the delete_input_files setting is properly loaded."""

    # Create a temporary config file for testing
    test_config_content = """
[DEFAULT]
provider = gemini
model = gemini-2.5-flash-lite
base_url = https://generativelanguage.googleapis.com/v1beta
temperature = 0.7
max_tokens = 2048
top_p = 0.9
thinking_enabled = false
search_enabled = false
retry_attempts = 3
retry_delay = 2
api_host = 0.0.0.0
api_port = 8000
api_workers = 1
monitor_interval = 5
file_timeout = 30
delete_input_files = false
output_format = markdown
output_directory = /tmp/test_output

[gemini]
# Gemini specific settings

[test_folder]
folder_path = /tmp/test_input
enabled = true
system_prompt = Test system prompt
user_prompt_template = Test user prompt: {content}
provider = gemini
model = gemini-2.5-flash-lite
temperature = 0.5
max_tokens = 1024
output_format = markdown
"""

    # Write test config
    test_config_path = Path(__file__).parent / "test_config.ini"
    with open(test_config_path, "w") as f:
        f.write(test_config_content)

    try:
        # Test with delete_input_files = false
        config_manager = ConfigManager(test_config_path)
        settings = config_manager.load_config()

        print(f"delete_input_files setting: {settings.file_monitor.delete_input_files}")

        if settings.file_monitor.delete_input_files == False:
            print("✅ SUCCESS: delete_input_files setting correctly loaded as False")
        else:
            print(
                f"❌ FAIL: Expected False, got {settings.file_monitor.delete_input_files}"
            )

        # Test default value (True)
        test_config_content_default = test_config_content.replace(
            "delete_input_files = false", "# delete_input_files = false"
        )
        with open(test_config_path, "w") as f:
            f.write(test_config_content_default)

        config_manager_default = ConfigManager(test_config_path)
        settings_default = config_manager_default.load_config()

        print(
            f"Default delete_input_files setting: {settings_default.file_monitor.delete_input_files}"
        )

        if settings_default.file_monitor.delete_input_files == True:
            print("✅ SUCCESS: delete_input_files default value is True")
        else:
            print(
                f"❌ FAIL: Expected True, got {settings_default.file_monitor.delete_input_files}"
            )

    finally:
        # Clean up
        if test_config_path.exists():
            test_config_path.unlink()


if __name__ == "__main__":
    test_delete_input_files_setting()

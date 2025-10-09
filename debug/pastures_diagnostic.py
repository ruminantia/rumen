#!/usr/bin/env python3
"""
Diagnostic script for debugging pastures folder monitoring in Rumen.
This script helps identify why files in /app/pastures are not being processed.
"""

import os
import sys
import time
from pathlib import Path
import logging

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import get_settings, Settings
from file_monitor import FileMonitor, FileProcessor

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def check_pastures_folder():
    """Check if pastures folder exists and is accessible."""
    pastures_path = Path("/app/pastures")

    print(f"\n=== Checking pastures folder: {pastures_path} ===")

    if not pastures_path.exists():
        print(f"❌ ERROR: Pastures folder does not exist: {pastures_path}")
        return False

    if not pastures_path.is_dir():
        print(f"❌ ERROR: Pastures path is not a directory: {pastures_path}")
        return False

    print(f"✅ Pastures folder exists and is a directory")

    # Check permissions
    if not os.access(pastures_path, os.R_OK):
        print(f"❌ ERROR: No read permission for pastures folder: {pastures_path}")
        return False
    if not os.access(pastures_path, os.W_OK):
        print(f"⚠️  WARNING: No write permission for pastures folder: {pastures_path}")

    print(f"✅ Read permission confirmed")
    return True


def list_pastures_files():
    """List all files in pastures folder recursively."""
    pastures_path = Path("/app/pastures")

    print(f"\n=== Listing files in pastures folder (recursive) ===")

    all_files = []
    for root, dirs, files in os.walk(pastures_path):
        for file in files:
            file_path = Path(root) / file
            all_files.append(file_path)
            print(f"📄 {file_path.relative_to(pastures_path)}")

    if not all_files:
        print("❌ No files found in pastures folder")
        return []

    print(f"✅ Found {len(all_files)} files total")
    return all_files


def check_file_processing_eligibility():
    """Check which files would be processed by the current configuration."""
    pastures_path = Path("/app/pastures")

    print(f"\n=== Checking file processing eligibility ===")

    # Create a mock file processor to test eligibility
    settings = get_settings()
    processor = FileProcessor(lambda x, y, z: True, settings)

    eligible_files = []
    ineligible_files = []

    for root, dirs, files in os.walk(pastures_path):
        for file in files:
            file_path = Path(root) / file

            if processor.should_process_file(file_path):
                eligible_files.append(file_path)
                print(f"✅ Eligible: {file_path.relative_to(pastures_path)}")
            else:
                ineligible_files.append(file_path)
                print(f"❌ Ineligible: {file_path.relative_to(pastures_path)}")

    print(f"\n📊 Summary:")
    print(f"   Eligible files: {len(eligible_files)}")
    print(f"   Ineligible files: {len(ineligible_files)}")

    return eligible_files, ineligible_files


def check_configuration():
    """Check if pastures is properly configured."""
    print(f"\n=== Checking configuration ===")

    try:
        settings = get_settings()

        # Check if pastures folder is configured
        if "pastures" not in settings.folders:
            print("❌ ERROR: 'pastures' section not found in configuration")
            return False

        pastures_config = settings.folders["pastures"]

        print(f"✅ Pastures configuration found:")
        print(f"   - Folder path: {pastures_config.folder_path}")
        print(f"   - Enabled: {pastures_config.enabled}")
        print(f"   - Model: {pastures_config.model}")
        print(f"   - Provider: {pastures_config.provider}")

        if not pastures_config.enabled:
            print("❌ ERROR: Pastures folder is not enabled in configuration")
            return False

        if pastures_config.folder_path != Path("/app/pastures"):
            print(
                f"⚠️  WARNING: Folder path mismatch. Expected: /app/pastures, Got: {pastures_config.folder_path}"
            )

        return True

    except Exception as e:
        print(f"❌ ERROR loading configuration: {e}")
        return False


def test_file_monitoring():
    """Test if file monitoring would work for pastures."""
    print(f"\n=== Testing file monitoring setup ===")

    try:
        settings = get_settings()

        # Check if pastures is in enabled folders
        enabled_folders = {
            name: config for name, config in settings.folders.items() if config.enabled
        }

        if "pastures" not in enabled_folders:
            print("❌ ERROR: Pastures is not in enabled folders")
            return False

        print(f"✅ Pastures is in enabled folders")
        print(f"   Total enabled folders: {len(enabled_folders)}")

        # Test folder creation
        pastures_path = Path("/app/pastures")
        try:
            pastures_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Can create/access pastures folder")
        except Exception as e:
            print(f"❌ ERROR creating pastures folder: {e}")
            return False

        return True

    except Exception as e:
        print(f"❌ ERROR testing file monitoring: {e}")
        return False


def check_recursive_monitoring():
    """Check if recursive monitoring is enabled."""
    print(f"\n=== Checking recursive monitoring ===")

    # This is hardcoded in the current implementation
    print("⚠️  IMPORTANT: Current implementation has recursive=False")
    print("   This means only files in the root /app/pastures folder will be monitored")
    print("   Files in subdirectories will NOT be automatically processed")

    pastures_path = Path("/app/pastures")
    subdir_files = []

    for root, dirs, files in os.walk(pastures_path):
        if root != str(pastures_path):  # Skip root directory
            for file in files:
                file_path = Path(root) / file
                subdir_files.append(file_path)

    if subdir_files:
        print(
            f"❌ Found {len(subdir_files)} files in subdirectories that won't be monitored:"
        )
        for file_path in subdir_files:
            print(f"   📄 {file_path.relative_to(pastures_path)}")
    else:
        print("✅ No files found in subdirectories")

    return len(subdir_files) > 0


def main():
    """Run all diagnostic checks."""
    print("🔍 Rumen Pastures Diagnostic Tool")
    print("=" * 50)

    results = {}

    # Run diagnostics
    results["folder_exists"] = check_pastures_folder()
    results["configuration"] = check_configuration()
    results["file_monitoring"] = test_file_monitoring()
    results["files_listed"] = list_pastures_files()
    results["eligible_files"] = check_file_processing_eligibility()
    results["recursive_issue"] = check_recursive_monitoring()

    # Summary
    print(f"\n" + "=" * 50)
    print("📋 DIAGNOSTIC SUMMARY")
    print("=" * 50)

    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check}")

    # Key findings
    print(f"\n🔑 KEY FINDINGS:")

    if results.get("recursive_issue"):
        print(
            "1. 🚨 RECURSIVE MONITORING DISABLED - Files in subdirectories won't be processed"
        )
        print("   Solution: Modify file_monitor.py to set recursive=True")

    if not results.get("folder_exists"):
        print("2. 🚨 PASTURES FOLDER ISSUE - Folder doesn't exist or inaccessible")

    if not results.get("configuration"):
        print("3. 🚨 CONFIGURATION ISSUE - Pastures not properly configured")

    if not any(results.values()):
        print("❌ Multiple issues detected. Check the detailed output above.")
    else:
        print("✅ Most checks passed. The main issue is likely recursive monitoring.")


if __name__ == "__main__":
    main()

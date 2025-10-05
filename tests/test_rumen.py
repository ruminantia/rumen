#!/usr/bin/env python3
"""
Test script to verify Rumen LLM API setup with authentication.
This script tests the basic functionality of the Rumen application.
"""

import os
import sys
import time
import json
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: 'requests' module not found.")
    print("Install it with: pip install requests")
    sys.exit(1)


class RumenTester:
    """Test suite for Rumen LLM API with authentication support."""

    def __init__(self, base_url="http://localhost:8000", api_key=None):
        self.base_url = base_url
        self.api_key = api_key or self._get_api_key_from_env()
        self.headers = (
            {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        )

    def _get_api_key_from_env(self):
        """Get API key from environment or .env file."""
        # Try environment variable first
        api_key = os.getenv("RUMEN_API_KEY")
        if api_key:
            return api_key

        # Try reading from .env file
        try:
            env_file = Path(".env")
            if env_file.exists():
                with open(env_file, "r") as f:
                    for line in f:
                        if line.startswith("RUMEN_API_KEY="):
                            return line.strip().split("=", 1)[1]
        except Exception:
            pass

        return None

    def test_api_root(self):
        """Test the API root endpoint (no authentication required)."""
        print("Testing API root endpoint...")
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Root endpoint: {data}")
                return True
            else:
                print(f"✗ Root endpoint failed: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"✗ Root endpoint failed: {e}")
            return False

    def test_api_health(self):
        """Test the API health endpoint (requires authentication)."""
        print("Testing API health endpoint...")
        try:
            response = requests.get(
                f"{self.base_url}/health", headers=self.headers, timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Health check passed: {data}")
                return True
            elif response.status_code == 403:
                print(
                    "✗ Health check failed: Authentication required (no API key provided)"
                )
                return False
            else:
                print(f"✗ Health check failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"✗ Health check failed: {e}")
            return False

    def test_process_endpoint(self):
        """Test the process endpoint with query parameters."""
        print("Testing process endpoint...")
        try:
            test_text = "The quick brown fox jumps over the lazy dog."
            params = {
                "text": test_text,
                "system_prompt": "You are a helpful assistant that analyzes text.",
                "user_prompt": "Please analyze this text: {content}",
                "temperature": 0.3,
                "max_tokens": 100,
                "output_format": "markdown",
            }

            response = requests.post(
                f"{self.base_url}/process",
                params=params,
                headers=self.headers,
                timeout=30,
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Process endpoint: Successfully processed text")
                print(f"  Output file: {data.get('output_file')}")
                print(f"  Content length: {data.get('content_length')}")
                return True
            elif response.status_code == 403:
                print("✗ Process endpoint failed: Authentication required")
                return False
            else:
                print(f"✗ Process endpoint failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"✗ Process endpoint failed: {e}")
            return False

    def test_folders_endpoint(self):
        """Test the folders endpoint."""
        print("Testing folders endpoint...")
        try:
            response = requests.get(
                f"{self.base_url}/folders", headers=self.headers, timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Folders endpoint: Found {data.get('total_folders')} folders")
                print(f"  Enabled folders: {data.get('enabled_folders')}")
                return True
            elif response.status_code == 403:
                print("✗ Folders endpoint failed: Authentication required")
                return False
            else:
                print(f"✗ Folders endpoint failed: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"✗ Folders endpoint failed: {e}")
            return False

    def test_file_monitor_status(self):
        """Test the file monitor status endpoint."""
        print("Testing file monitor status...")
        try:
            response = requests.get(
                f"{self.base_url}/file-monitor/status", headers=self.headers, timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✓ File monitor status: {data}")
                return True
            elif response.status_code == 403:
                print("✗ File monitor status failed: Authentication required")
                return False
            else:
                print(f"✗ File monitor status failed: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"✗ File monitor status failed: {e}")
            return False

    def test_results_endpoint(self):
        """Test the results endpoint."""
        print("Testing results endpoint...")
        try:
            response = requests.get(
                f"{self.base_url}/results?limit=5", headers=self.headers, timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                print(
                    f"✓ Results endpoint: Found {data.get('total_results')} total results"
                )
                print(f"  Showing: {len(data.get('results', []))} recent results")
                return True
            elif response.status_code == 403:
                print("✗ Results endpoint failed: Authentication required")
                return False
            else:
                print(f"✗ Results endpoint failed: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"✗ Results endpoint failed: {e}")
            return False

    def test_file_processing(self):
        """Test file processing by creating a test file in input directory."""
        print("Testing file processing...")
        try:
            # Create test input directory if it doesn't exist
            input_dir = Path("input")
            input_dir.mkdir(exist_ok=True)

            # Create a test markdown file
            test_file = input_dir / "test_article.md"
            test_content = """# Test Article

This is a test article for Rumen file processing.
It contains some sample content that should be processed by the LLM.

The quick brown fox jumps over the lazy dog.
Artificial intelligence is transforming many industries.
"""

            with open(test_file, "w") as f:
                f.write(test_content)

            print(f"✓ Created test file: {test_file}")
            print(
                "ℹ Note: File processing test requires folder monitoring to be enabled in config.ini"
            )
            print(
                "ℹ Currently this only verifies file creation, not automatic processing"
            )

            return True

        except Exception as e:
            print(f"✗ File processing test failed: {e}")
            return False

    def test_authentication_required(self):
        """Test that endpoints require authentication."""
        print("Testing authentication requirements...")
        endpoints_to_test = [
            "/health",
            "/folders",
            "/results?limit=1",
            "/file-monitor/status",
        ]

        all_protected = True
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code != 403:
                    print(
                        f"✗ Endpoint {endpoint} should require authentication but returned {response.status_code}"
                    )
                    all_protected = False
                else:
                    print(f"✓ Endpoint {endpoint} correctly requires authentication")
            except Exception as e:
                print(f"✗ Error testing {endpoint}: {e}")
                all_protected = False

        return all_protected

    def run_all_tests(self):
        """Run all tests and return results."""
        print("Rumen Test Suite")
        print("=" * 50)

        if not self.api_key:
            print("⚠ No API key found!")
            print("Set RUMEN_API_KEY environment variable or add it to .env file")
            print("You can get your API key with: ./run-docker.sh api-key")
            print()

        # Check if API is running
        print("Checking if Rumen API is running...")

        tests = [
            self.test_api_root,
            self.test_authentication_required,
            self.test_api_health,
            self.test_folders_endpoint,
            self.test_file_monitor_status,
            self.test_results_endpoint,
            self.test_process_endpoint,
            self.test_file_processing,
        ]

        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
                print()
            except Exception as e:
                print(f"✗ Test {test.__name__} crashed: {e}")
                results.append(False)
                print()

        passed = sum(results)
        total = len(results)

        print("=" * 50)
        print(f"Test Results: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed! Rumen is working correctly.")
            return 0
        else:
            print("⚠ Some tests failed. Check the logs above for details.")
            if not self.api_key:
                print(
                    "💡 Tip: Most tests require an API key. Set RUMEN_API_KEY environment variable."
                )
            return 1


def main():
    """Main entry point."""
    # Allow custom API key via command line
    import argparse

    parser = argparse.ArgumentParser(description="Test Rumen LLM API")
    parser.add_argument("--api-key", help="Rumen API key for authentication")
    parser.add_argument(
        "--url", default="http://localhost:8000", help="Rumen API base URL"
    )
    args = parser.parse_args()

    tester = RumenTester(base_url=args.url, api_key=args.api_key)
    return tester.run_all_tests()


if __name__ == "__main__":
    sys.exit(main())

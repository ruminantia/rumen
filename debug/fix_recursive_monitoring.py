#!/usr/bin/env python3
"""
Solution script to enable recursive monitoring for pastures folder.
This script provides both immediate fixes and long-term solutions.
"""

import os
import sys
from pathlib import Path


def create_immediate_solution():
    """Create a temporary solution by moving files to root folder."""
    pastures_path = Path("/app/pastures")

    print("=== Creating Immediate Solution ===")

    # Find all markdown files recursively
    all_files = []
    for root, dirs, files in os.walk(pastures_path):
        for file in files:
            if file.endswith((".md", ".markdown", ".txt")):
                file_path = Path(root) / file
                all_files.append(file_path)

    if not all_files:
        print("❌ No processable files found in pastures folder")
        return

    print(f"Found {len(all_files)} processable files")

    # Move files to root pastures folder
    moved_count = 0
    for file_path in all_files:
        try:
            # Create new filename that preserves directory structure info
            relative_path = file_path.relative_to(pastures_path)
            new_filename = str(relative_path).replace("/", "_").replace("\\", "_")
            new_path = pastures_path / new_filename

            # Skip if already in root
            if file_path.parent == pastures_path:
                continue

            # Move file
            file_path.rename(new_path)
            print(f"✅ Moved: {relative_path} -> {new_filename}")
            moved_count += 1

        except Exception as e:
            print(f"❌ Failed to move {file_path}: {e}")

    print(f"\n📊 Moved {moved_count} files to root folder")
    return moved_count


def show_permanent_fix():
    """Show how to permanently fix the recursive monitoring issue."""
    print("\n=== Permanent Fix Instructions ===")
    print("\nTo permanently enable recursive monitoring, modify file_monitor.py:")
    print("\n1. Edit rumen/src/file_monitor.py")
    print("2. Find line with 'recursive=False' (around line 154)")
    print("3. Change it to 'recursive=True'")
    print("\nThe line should look like this:")
    print("""
    self.observer.schedule(
        event_handler,
        str(folder_path),
        recursive=True,  # Enable recursive monitoring
    )
    """)

    print("\n4. Also update the existing file processing to handle subdirectories:")
    print("""
    In the process_existing_files() method, replace the file glob patterns with:

    # Process all markdown files recursively
    for file_path in folder_path.rglob("*.md"):
        if self.file_processor.should_process_file(file_path):
            self._process_file_sync(file_path, folder_config)

    for file_path in folder_path.rglob("*.markdown"):
        if self.file_processor.should_process_file(file_path):
            self._process_file_sync(file_path, folder_config)

    for file_path in folder_path.rglob("*.txt"):
        if self.file_processor.should_process_file(file_path):
            self._process_file_sync(file_path, folder_config)
    """)


def create_patch_file():
    """Create a patch file for the permanent fix."""
    patch_content = """--- a/src/file_monitor.py
+++ b/src/file_monitor.py
@@ -151,7 +151,7 @@ class FileMonitor:
             self.observer.schedule(
                 event_handler,
                 str(folder_path),
-                recursive=False,  # Don't watch subdirectories
+                recursive=True,  # Enable recursive monitoring
             )
             logger.info(f"Started monitoring folder: {folder_path}")
         except Exception as e:
@@ -173,15 +173,15 @@ class FileMonitor:
             logger.info(f"Processing existing files in: {folder_path}")

             try:
-                # Process all markdown files in the folder
-                for file_path in folder_path.glob("*.md"):
+                # Process all markdown files recursively
+                for file_path in folder_path.rglob("*.md"):
                     if self.file_processor.should_process_file(file_path):
                         self._process_file_sync(file_path, folder_config)

-                for file_path in folder_path.glob("*.markdown"):
+                for file_path in folder_path.rglob("*.markdown"):
                     if self.file_processor.should_process_file(file_path):
                         self._process_file_sync(file_path, folder_config)

-                for file_path in folder_path.glob("*.txt"):
+                for file_path in folder_path.rglob("*.txt"):
                     if self.file_processor.should_process_file(file_path):
                         self._process_file_sync(file_path, folder_config)
"""

    patch_path = Path(__file__).parent / "recursive_monitoring.patch"
    with open(patch_path, "w") as f:
        f.write(patch_content)

    print(f"\n📝 Patch file created: {patch_path}")
    print("Apply it with: patch -p1 < debug/recursive_monitoring.patch")


def main():
    """Main function to provide solutions."""
    print("🔧 Rumen Recursive Monitoring Solution")
    print("=" * 50)

    # Check if we're in the right environment
    pastures_path = Path("/app/pastures")
    if not pastures_path.exists():
        print("❌ ERROR: /app/pastures folder not found")
        print("Make sure you're running this inside the rumen container")
        sys.exit(1)

    print("\nChoose a solution:")
    print("1. Immediate fix - Move files to root folder")
    print("2. Show permanent fix instructions")
    print("3. Create patch file for permanent fix")
    print("4. All of the above")

    try:
        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            create_immediate_solution()
        elif choice == "2":
            show_permanent_fix()
        elif choice == "3":
            create_patch_file()
        elif choice == "4":
            create_immediate_solution()
            show_permanent_fix()
            create_patch_file()
        else:
            print("❌ Invalid choice")

    except KeyboardInterrupt:
        print("\n👋 Operation cancelled")

    print(
        "\n✅ Solution provided. Remember to restart the rumen container after making changes."
    )


if __name__ == "__main__":
    main()

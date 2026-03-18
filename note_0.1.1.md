## Summary

This release adds the ability to save iOS device screenshots directly to disk, so you can persist screenshots to a file path of your choice instead of only receiving them in memory.

## What's new compared to 0.1.0

### New MCP tool: Save screenshot to disk

- **`ios_save_screenshot_to_disk(absolute_image_path)`**  
  Saves a screenshot of the currently selected iOS device to a file at the given absolute path.
  - Path must end with `.png`.
  - Parent directories are created if they don’t exist.
  - Fails if the file already exists (no overwrite).

This complements the existing `ios_screenshot` tool (which returns image content in memory) and is useful when you need to store screenshots on the host filesystem for later use or inspection.

## Upgrade

- **From PyPI:** `pip install --upgrade idb-mcp`
- **From source:** pull the `v0.1.1` tag and reinstall.

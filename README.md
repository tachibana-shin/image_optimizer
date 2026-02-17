# Image Optimizer for Calibre

![Image Optimizer](./images/icon.png)

**Image Optimizer** is a Calibre plugin that allows you to batch compress and optimize images within your eBooks (EPUB/ZIP/AZW3/MOBI/CBZ/CBR...) to reduce file size without significant loss of quality.

## Why Image Optimizer?

Compared to other plugins like [*Bulk Image Resizer*](https://github.com/akupiec/calibre_plugin_bulk-img-resizer), this plugin offers:
- **Superior Compression**: Uses advanced optimization algorithms to achieve significantly smaller output files while maintaining visual fidelity.
- **Deep Optimization**: While it may take slightly longer to process due to intensive compression techniques, the trade-off is a much more efficient storage reduction.
- **Extreme Compatibility**: Detects images by "magic bytes" (file headers), allowing it to optimize files even if they have incorrect or missing extensions—something most basic resizers cannot do.
- **Modern Format Support**: Extends beyond JPG/PNG to support AVIF, WebP, QOI, HDR, and many others.

## Features

- **Batch Processing**: Select multiple books and optimize them in one go.
- **Smart Detection**: Automatically detects image formats based on file content (magic bytes), supporting files even with missing or incorrect extensions.
- **Supported Formats**: Handles a wide range of formats including JPEG, PNG, WEBP, GIF, BMP, TIFF, ICO, AVIF, QOI, HDR, OpenEXR, DDS, Farbfeld, and PNM.
- **Configurable**: Set target resolution, quality, and format conversion preferences.
- **Non-Destructive**: Creates a new book entry with the optimized files, keeping your originals safe.
- **Multilingual**: Supports English, Vietnamese, and Japanese.

## Preview

- File number 1 is optimized for full HD with configuration `size=1080, quality=85`
- File number 2 is optimized for Kindle with configuration `size=400, quality=85`
- File number 3 is the original file
<img width="1365" height="767" alt="image" src="https://github.com/user-attachments/assets/da7e7405-b571-4ae3-8a48-07431d51b15f" />


## Installation

1. Download the `image_optimizer.zip` release.
2. Open **Calibre**.
3. Go to **Preferences** -> **Plugins**.
4. Click **Load plugin from file** and select the downloaded zip file.
5. Restart **Calibre**.

### Adding to Toolbar
If the icon does not appear automatically after restarting:
1. Go to **Preferences** -> **Interface** -> **Toolbars & menus**.
2. Select **The main toolbar** from the dropdown menu.
3. Locate **Image Optimizer** in the left column (**Available actions**).
4. Click the **Right Arrow** button to move it to the right column (**Current actions**).
5. Click **Apply**.

## Usage

1. Select one or more books in your Calibre library.
2. Click the **Image Optimizer** icon in the toolbar.
3. Configure your optimization settings (Size, Quality, etc.) in the dialog that appears.
4. Click **OK** to start the optimization process.
   - The plugin will verify image headers to ensure correct processing.
   - A new book entry will be created with the optimized version.
   - A summary report will show the total space reduction achieved.

## Development

### Prerequisites

- Python 3
- Calibre (installed and added to PATH)
- `pybabel` (for translations)

### Build Commands

The project uses a `Makefile` for build automation:

- **Build Plugin**:

  ```bash
  make all
  ```

  This compiles translations and creates the `image_optimizer.zip` file.

- **Compile Translations**:

  ```bash
  make translate
  ```

- **Load into Calibre (Dev)**:

  ```bash
  make load
  ```

  _Note: `make load` uses `clear` which is Unix-specific. On Windows, you may need to adjust this or manually install._

- **Debug Mode**:

  ```bash
  make dev
  ```

  Loads the plugin and launches Calibre in debug mode (`calibre-debug -g`).

- **Clean**:
  ```bash
  make clean
  ```
  Removes the generated zip file.

## Author

**Tachibana Shin**

## License

[License Type] (e.g., GPL-3.0)

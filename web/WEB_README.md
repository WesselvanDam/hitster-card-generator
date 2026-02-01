# Card PDF Generator - Web Version

A static website that generates printable card PDFs from CSV data using PyScript.

## Features

- **No Server Required**: Runs entirely in the browser using PyScript
- **CSV Upload**: Upload your card data in CSV format
- **Validation**: Automatic validation of CSV format and configuration
- **Customizable**: Adjust all card dimensions, margins, and colors
- **User-Friendly**: Clear instructions and helpful error messages
- **Instant Download**: Generate and download PDF directly from the browser

## Usage

1. Open `index.html` in a modern web browser
2. Upload a CSV file with your card data
3. Adjust configuration settings if needed (optional)
4. Click "Generate PDF" to create and download your cards

## CSV Format Requirements

Your CSV file must include the following columns:

- **type**: Card type (must be one of: song, video, article, painting, or back)
- **url**: URL for the QR code on the back of the card
- **top**: Text displayed at the top of the card
- **center**: Large text in the center (can be empty)
- **bottom**: Text displayed at the bottom of the card

### Example CSV:

```csv
type;url;top;bottom;center
song;https://open.spotify.com/track/4PTG3Z6ehGkBFwjybzWkR8;Rick Astley;Never Gonna Give You Up;1987
video;https://www.youtube.com/watch?v=xuCn8ux2gbs;bill wurtz;history of the entire world, i guess;2017
article;https://www.example.com/article;Author Name;Article Title;2023
painting;https://example.com/image.jpg;Vincent van Gogh;The Starry Night;1889
```

## Configuration Options

### Card Settings

- **Bleed**: The area outside the page that is cut off during printing (default: 3mm)
- **Card Size**: The size of each card (default: 66mm)
- **Card Gap**: Space between cards (default: 3mm)
- **Card Margin**: Margin around the card layout (default: 3mm)

### Token Settings

- **Token Size**: Size of game tokens (default: 28mm)
- **Token Gap**: Space between tokens (default: 6mm)
- **Token Margin**: Margin around token layout (default: 6mm)

### Colors

Each card type has customizable background and text colors:

- Back card (for QR codes)
- Song cards
- Video cards
- Article cards
- Painting cards

## Technical Details

- Built with [PyScript](https://pyscript.net/)
- Uses FPDF2 for PDF generation
- QR codes generated with the qrcode library
- Data handling with pandas
- Runs entirely client-side - no data is sent to any server

## Browser Compatibility

Requires a modern web browser with WebAssembly support:

- Chrome/Edge 90+
- Firefox 88+
- Safari 15+

## Notes

- For A4 paper (210mm x 297mm), the default settings are optimized
- Card and token configurations must fit evenly into the page width
- The validation will notify you if dimensions don't align properly
- Tokens require a token.png file in the assets/ folder (not included in web version)

## Development

To modify the PDF generation logic, edit `web_pdf_generator.py`.
To change the interface, edit `index.html`.
Configuration is stored in `pyscript.toml`.

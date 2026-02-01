# How to Use the Card PDF Generator Website

## Quick Start

1. **Open the website**: Double-click `index.html` or open it in your web browser
   - If opening directly doesn't work (due to browser security), use a local web server:
     - Python: `python -m http.server 8000` then visit `http://localhost:8000`
     - Node.js: `npx http-server` then visit the provided URL

2. **First Load**: The website will download PyScript and required Python packages (pandas, fpdf2, qrcode, pillow). This may take a minute on first load.

3. **Upload CSV**: Click "Choose File" and select your CSV file
   - The file will be validated automatically
   - You'll see an error message if the format is incorrect

4. **Configure (Optional)**: Adjust card dimensions and colors if needed
   - Default settings work for A4 paper (210mm x 297mm)

5. **Generate**: Click "Generate PDF" button
   - PDF will be generated in your browser
   - Download will start automatically

## Troubleshooting

### PyScript Loading Issues

- Make sure you have an internet connection (PyScript loads from CDN)
- Clear your browser cache and reload the page
- Try a different browser (Chrome, Firefox, Edge recommended)

### CSV Upload Errors

**"Missing required columns"**

- Ensure your CSV has: type, url, top, center, bottom

**"Invalid card types found"**

- Type must be one of: song, video, article, painting, back

**"URL/Top/Bottom column cannot contain empty values"**

- All rows must have values in these columns
- Center can be empty

### Configuration Errors

**"Invalid card configuration"**

- Card size + gap must fit evenly in 210mm width
- Try the default values: size=66mm, gap=3mm, margin=3mm

**"Invalid token configuration"**

- Token size + gap must fit evenly in 210mm width
- Try the default values: size=28mm, gap=6mm, margin=6mm

### PDF Generation Errors

- Make sure CSV is uploaded and validated first
- Check browser console (F12) for detailed error messages
- Try with a smaller CSV file to test

## Tips

- Start with the provided `data/data.csv` as a template
- Keep your CSV file simple - use semicolon (;) or comma (,) as separator
- Test with a small dataset first (3-5 rows)
- Export CSV from Excel using "CSV (Semicolon delimited)" format
- The website works offline after first load (packages are cached)

## Browser Compatibility

Tested and working on:

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Edge 90+
- ✅ Safari 15+

Not supported:

- ❌ Internet Explorer
- ❌ Older mobile browsers

## Privacy

All processing happens in your browser - no data is sent to any server!

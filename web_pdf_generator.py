import csv
import io
from js import document, Uint8Array, Blob, URL
from pyodide.ffi import create_proxy
import math
from fpdf import FPDF
import qrcode


# Global variables to store configuration
config = {}
csv_data = None

# Default colors for common card categories
DEFAULT_COLORS = {
    "song": {"bg": "#8cbeb2", "text": "#192623"},
    "video": {"bg": "#f3b562", "text": "#33230e"},
    "article": {"bg": "#f06060", "text": "#320e0e"},
    "painting": {"bg": "#f2ebbf", "text": "#333126"},
}


def rgb_from_hex(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def show_error(message):
    """Display an error message to the user."""
    from js import window

    window.showAlert(message, "error")


def show_success(message):
    """Display a success message to the user."""
    from js import window

    window.showAlert(message, "success")


def show_status(message):
    """Display a status message to the user."""
    from js import window

    window.showAlert(message, "status")


def generate_card_type_colors(card_types):
    """Generate color pickers for each unique card type found in the CSV."""
    container = document.getElementById("dynamic-card-types")
    container.innerHTML = ""  # Clear existing color pickers

    # Hide the "no CSV" message
    no_csv_msg = document.getElementById("no-csv-message")
    if no_csv_msg:
        no_csv_msg.classList.add("hidden")

    # Generate color picker for each card type
    for card_type in sorted(card_types):
        # Get default colors or generate random ones
        default_colors = DEFAULT_COLORS.get(
            card_type, {"bg": "#cccccc", "text": "#000000"}
        )

        # Create the HTML structure for background color
        bg_div = document.createElement("div")

        bg_label = document.createElement("span")
        bg_label.className = "font-medium text-slate-700 dark:text-slate-300"
        bg_label.textContent = f"{card_type.capitalize()} BG"
        bg_div.appendChild(bg_label)

        bg_input = document.createElement("input")
        bg_input.type = "color"
        bg_input.className = "ring-2 ring-slate-200 dark:ring-slate-600 rounded-full"
        bg_input.id = f"{card_type}-bg"
        bg_input.value = default_colors["bg"]
        bg_div.appendChild(bg_input)

        container.appendChild(bg_div)

        # Create the HTML structure for text color
        text_div = document.createElement("div")

        text_label = document.createElement("span")
        text_label.className = "font-medium text-slate-700 dark:text-slate-300"
        text_label.textContent = f"{card_type.capitalize()} Text"
        text_div.appendChild(text_label)

        text_input = document.createElement("input")
        text_input.type = "color"
        text_input.className = "ring-2 ring-slate-200 dark:ring-slate-600 rounded-full"
        text_input.id = f"{card_type}-text"
        text_input.value = default_colors["text"]
        text_div.appendChild(text_input)

        container.appendChild(text_div)


def validate_csv_data(data):
    """Validate that the CSV data has the required columns and valid values."""
    required_columns = ["type", "url", "top", "center", "bottom"]

    if not data:
        return False, "CSV data is empty"

    # Check if all required columns exist
    missing_columns = [col for col in required_columns if col not in data[0].keys()]
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"

    # Check required fields are not empty (center can be empty)
    for idx, row in enumerate(data, start=1):
        if not str(row.get("type", "")).strip():
            return False, f"Type column cannot contain empty values (row {idx})"
        if not str(row.get("url", "")).strip():
            return False, f"URL column cannot contain empty values (row {idx})"
        if not str(row.get("top", "")).strip():
            return False, f"Top column cannot contain empty values (row {idx})"
        if not str(row.get("bottom", "")).strip():
            return False, f"Bottom column cannot contain empty values (row {idx})"

    return True, "CSV data is valid"


def validate_config(config):
    """Validate that the configuration is valid (basic server-side check)."""
    # Note: Main validation is done on the frontend in JavaScript
    # This is a backup validation in case JavaScript is disabled or bypassed

    # Check if all values are positive
    for key, value in config.items():
        if key.startswith("CARD_COLORS"):
            continue
        if value < 0:
            return False, f"Configuration value '{key}' must be positive"

    return True, "Configuration is valid"


async def load_csv_file(event):
    """Load and validate the CSV file."""
    global csv_data

    file_list = event.target.files
    if not file_list.length:
        return

    file = file_list.item(0)

    # Read file content
    array_buffer = await file.arrayBuffer()
    bytes_data = bytes(Uint8Array.new(array_buffer))

    try:
        # Try to read the CSV with automatic delimiter detection
        text_data = bytes_data.decode("utf-8", errors="replace")
        sample = text_data[:4096]
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=[",", ";", "\t", "|"])
        except csv.Error:
            dialect = csv.excel

        reader = csv.DictReader(io.StringIO(text_data), dialect=dialect)
        csv_data = [
            row for row in reader if any((v or "").strip() for v in row.values())
        ]

        # Validate the CSV data
        is_valid, message = validate_csv_data(csv_data)
        if not is_valid:
            show_error(f"CSV validation failed: {message}")
            csv_data = None
            return

        # Get unique card types (excluding 'back' if present)
        unique_types = sorted(
            {row["type"] for row in csv_data if row.get("type") != "back"}
        )

        # Generate color pickers for each type
        generate_card_type_colors(unique_types)

        show_success(
            f"CSV file loaded successfully! Found {len(csv_data)} cards with {len(unique_types)} unique type(s): {', '.join(sorted(unique_types))}."
        )

    except Exception as e:
        show_error(
            f"Error reading CSV file: {str(e)}. Please ensure your file is in CSV format with semicolon or comma separators."
        )
        # Reset the input value to allow re-upload
        document.getElementById("csv-file").value = ""
        # Reset the csv_data variable
        csv_data = None


def create_card_front(record, pdf, config):
    """Creates a square card with the record data."""
    CARD_SIZE = config["CARD_SIZE"]
    COLOR = config["CARD_COLORS"][record["type"]]

    card_x = pdf.get_x()
    card_y = pdf.get_y()
    pdf.set_fill_color(*COLOR["bg"])
    pdf.rect(pdf.get_x(), pdf.get_y(), CARD_SIZE, CARD_SIZE, style="F")
    pdf.set_fill_color(255, 255, 255)

    # Place the center in the center of the card
    if str(record.get("center", "")).strip():
        pdf.set_text_color(*COLOR["text"])
        pdf.set_font(size=48, style="B")
        pdf.set_xy(card_x + (CARD_SIZE / 2), card_y + CARD_SIZE / 2 - pdf.font_size / 2)
        pdf.cell(CARD_SIZE, None, str(record["center"]), align="X")

    # Place the top text above the center
    pdf.set_font(size=14, style="B")
    pdf.set_xy(card_x + (CARD_SIZE / 2), card_y + 6)
    pdf.multi_cell(CARD_SIZE - 4, None, record["top"], align="X")

    # Place the bottom text below the center
    if str(record.get("bottom", "")).strip():
        pdf.set_font(style="I")
        pdf.set_xy(card_x + (CARD_SIZE / 2), card_y + CARD_SIZE - 14)
        pdf.multi_cell(CARD_SIZE - 4, None, record["bottom"], align="X")


def create_card_back(record, pdf, config):
    """Creates a square card showing a QR code of the 'url' property of the record."""
    CARD_SIZE = config["CARD_SIZE"]
    COLOR = config["CARD_COLORS"]["back"]

    card_x = pdf.get_x()
    card_y = pdf.get_y()
    pdf.set_fill_color(*COLOR["bg"])
    pdf.rect(pdf.get_x(), pdf.get_y(), CARD_SIZE, CARD_SIZE, style="F")
    pdf.set_fill_color(0, 0, 0)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr.add_data(record["url"])
    qr.make(fit=True)
    img = qr.make_image(fill_color=COLOR["text"], back_color="transparent")

    # Convert QR code to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    # Add image to PDF
    pdf.image(img_bytes, card_x + 1, card_y + 1, CARD_SIZE - 1, CARD_SIZE - 1)


def create_pdf_bytes(data, config):
    """Creates a PDF with the data from the DataFrame and returns it as bytes."""
    PAPER_WIDTH = config["PAPER_WIDTH"]
    PAPER_HEIGHT = config["PAPER_HEIGHT"]
    BLEED = config["BLEED"]
    CARD_SIZE = config["CARD_SIZE"]
    GAP = config["GAP"]
    CARD_MARGIN = config["CARD_MARGIN"]

    pdf = FPDF(format=[PAPER_WIDTH + 2 * BLEED, PAPER_HEIGHT + 2 * BLEED], unit="mm")
    pdf.set_font("Helvetica", size=12)
    pdf.set_margins(
        BLEED + CARD_MARGIN,
        BLEED + CARD_MARGIN,
        BLEED + CARD_MARGIN,
    )

    # Calculate the number of columns and rows that fit on the page.
    n_columns = int((PAPER_WIDTH - 2 * CARD_MARGIN + GAP) // (CARD_SIZE + GAP))
    n_rows_per_page = int((PAPER_HEIGHT - 2 * CARD_MARGIN + GAP) // (CARD_SIZE + GAP))
    n_rows = math.ceil(len(data) / n_columns)

    # Calculate the number of pages needed.
    n_pages = math.ceil(n_rows / n_rows_per_page)

    for page in range(n_pages):
        # Get the cards for this page.
        start_idx = page * n_rows_per_page * n_columns
        end_idx = (page + 1) * n_rows_per_page * n_columns
        cards_on_page = data[start_idx:end_idx]
        pdf.add_page()

        # Create the front of the cards, starting at the top left corner of the page
        for i in range(n_columns):
            row_x = pdf.get_x()
            row_y = pdf.get_y()
            for j in range(n_rows_per_page):
                idx = i + j * n_columns
                if idx >= len(cards_on_page):
                    break
                record = cards_on_page[idx]
                # Set the position of the card
                pdf.set_xy(row_x, row_y + j * CARD_SIZE + j * GAP)
                create_card_front(record, pdf, config)
            # Set the position for the next row
            pdf.set_xy(row_x + CARD_SIZE + GAP, row_y)

        pdf.add_page()
        # Create the back of the cards, starting at the top right corner of the page
        # This is necessary for double-sided printing.
        for i in reversed(range(n_columns)):
            row_x = pdf.get_x()
            row_y = pdf.get_y()
            for j in range(n_rows_per_page):
                idx = i + j * n_columns
                if idx >= len(cards_on_page):
                    break
                record = cards_on_page[idx]
                # Set the position of the card
                pdf.set_xy(row_x, row_y + j * CARD_SIZE + j * GAP)
                create_card_back(record, pdf, config)
            # Set the position for the next row
            pdf.set_xy(row_x + CARD_SIZE + GAP, row_y)

    return pdf.output()


def collect_config():
    """Collect configuration from the form inputs."""
    global csv_data
    config = {}

    # Numeric configuration
    config["PAPER_WIDTH"] = float(document.getElementById("paper-width").value)
    config["PAPER_HEIGHT"] = float(document.getElementById("paper-height").value)
    config["BLEED"] = float(document.getElementById("bleed").value)
    config["CARD_SIZE"] = float(document.getElementById("card-size").value)
    config["GAP"] = float(document.getElementById("gap").value)
    config["CARD_MARGIN"] = float(document.getElementById("card-margin").value)

    # Color configuration - always include back
    config["CARD_COLORS"] = {
        "back": {
            "bg": rgb_from_hex(document.getElementById("back-bg").value),
            "text": rgb_from_hex(document.getElementById("back-text").value),
        },
    }

    # Dynamically collect colors for card types found in CSV
    if csv_data is not None:
        unique_types = {row["type"] for row in csv_data if row.get("type") != "back"}
        for card_type in sorted(unique_types):
            bg_input = document.getElementById(f"{card_type}-bg")
            text_input = document.getElementById(f"{card_type}-text")
            if bg_input and text_input:
                config["CARD_COLORS"][card_type] = {
                    "bg": rgb_from_hex(bg_input.value),
                    "text": rgb_from_hex(text_input.value),
                }

    return config


def generate_pdf(event=None):
    """Generate the PDF from the loaded CSV data and configuration."""
    global csv_data

    # Check if CSV data is loaded
    if csv_data is None:
        show_error("Please upload a CSV file first.")
        return

    # Collect configuration
    try:
        config = collect_config()
    except Exception as e:
        show_error(f"Error reading configuration: {str(e)}")
        return

    # Validate configuration
    is_valid, message = validate_config(config)
    if not is_valid:
        show_error(message)
        return

    # Generate PDF
    try:
        show_status("Generating PDF... This may take a moment.")

        # Disable button during generation
        btn = document.getElementById("generate-btn")
        btn.disabled = True

        pdf_bytes = create_pdf_bytes(csv_data, config)

        # Create a download link
        pdf_array = Uint8Array.new(len(pdf_bytes))
        for i, b in enumerate(pdf_bytes):
            pdf_array[i] = b

        blob = Blob.new([pdf_array], {type: "application/pdf"})
        url = URL.createObjectURL(blob)

        # Create a temporary link and click it to download
        a = document.createElement("a")
        a.href = url
        a.download = "cards.pdf"
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)

        show_success(
            "PDF generated successfully! Your download should start automatically."
        )

        # Re-enable button
        btn.disabled = False

    except Exception as e:
        show_error(f"Error generating PDF: {str(e)}")
        # Re-enable button
        document.getElementById("generate-btn").disabled = False


# Set up event listeners
def setup():
    """Set up event listeners for the page."""
    file_input = document.getElementById("csv-file")
    file_input.addEventListener("change", create_proxy(load_csv_file))


# Make generatePDF available globally for the button onclick
from js import window

window.generatePDF = create_proxy(generate_pdf)

# Run setup when the script loads
setup()

// Global variables to store configuration
let csvData = null;

// Palette for card categories (400 as background, 950 as text)
const COLOR_PALETTE = [
  { bg: "#FF6466", text: "#480808" },
  { bg: "#FF8805", text: "#451305" },
  { bg: "#FFB800", text: "#481901" },
  { bg: "#FFC600", text: "#451F05" },
  { bg: "#A7E400", text: "#1D2E04" },
  { bg: "#31DE74", text: "#062E16" },
  { bg: "#00D393", text: "#002C22" },
  { bg: "#00D4BE", text: "#002F2E" },
  { bg: "#00D3F2", text: "#003345" },
  { bg: "#00BDFF", text: "#002F4A" },
  { bg: "#00A4FF", text: "#002655" },
  { bg: "#608AFF", text: "#131C4C" },
  { bg: "#9687FF", text: "#201267" },
  { bg: "#B57EFF", text: "#330A66" },
  { bg: "#E570FF", text: "#48054F" },
  { bg: "#FB67B5", text: "#520523" },
  { bg: "#FF647D", text: "#4E0318" },
  { bg: "#8CA1B9", text: "#000617" },
];

function getPaletteColor(index) {
  return COLOR_PALETTE[index % COLOR_PALETTE.length];
}

/**
 * Convert hex color to RGB object
 */
function rgbFromHex(hexColor) {
  const hex = hexColor.replace("#", "");
  return {
    r: parseInt(hex.substring(0, 2), 16),
    g: parseInt(hex.substring(2, 4), 16),
    b: parseInt(hex.substring(4, 6), 16),
  };
}

/**
 * Display an error message to the user
 */
function showError(message) {
  window.showAlert(message, "error");
}

/**
 * Display a success message to the user
 */
function showSuccess(message) {
  window.showAlert(message, "success");
}

/**
 * Display a status message to the user
 */
function showStatus(message) {
  console.log(message);
  window.showAlert(message, "status");
}

function yieldToBrowser() {
  return new Promise((resolve) => setTimeout(resolve, 0));
}

/**
 * Generate color pickers for each unique card type found in the CSV
 */
function generateCardTypeColors(cardTypes) {
  const container = document.getElementById("dynamic-card-types");
  container.innerHTML = ""; // Clear existing color pickers

  // Hide the "no CSV" message
  const noCsvMsg = document.getElementById("no-csv-message");
  if (noCsvMsg) {
    noCsvMsg.classList.add("hidden");
  }

  // Generate color picker for each card type
  cardTypes.sort().forEach((cardType, index) => {
    const defaultColors = getPaletteColor(index);

    // Create the HTML structure for background color
    const bgDiv = document.createElement("div");

    const bgLabel = document.createElement("span");
    bgLabel.className = "font-medium text-slate-700 dark:text-slate-300";
    bgLabel.textContent = `${cardType.charAt(0).toUpperCase() + cardType.slice(1)} BG`;
    bgDiv.appendChild(bgLabel);

    const bgInput = document.createElement("input");
    bgInput.type = "color";
    bgInput.className =
      "ring-2 ring-slate-200 dark:ring-slate-600 rounded-full w-10 h-10 shrink-0";
    bgInput.id = `${cardType}-bg`;
    bgInput.value = defaultColors.bg;
    bgDiv.appendChild(bgInput);

    container.appendChild(bgDiv);

    // Create the HTML structure for text color
    const textDiv = document.createElement("div");

    const textLabel = document.createElement("span");
    textLabel.className = "font-medium text-slate-700 dark:text-slate-300";
    textLabel.textContent = `${cardType.charAt(0).toUpperCase() + cardType.slice(1)} Text`;
    textDiv.appendChild(textLabel);

    const textInput = document.createElement("input");
    textInput.type = "color";
    textInput.className =
      "ring-2 ring-slate-200 dark:ring-slate-600 rounded-full w-10 h-10 shrink-0";
    textInput.id = `${cardType}-text`;
    textInput.value = defaultColors.text;
    textDiv.appendChild(textInput);

    container.appendChild(textDiv);
  });
}

/**
 * Validate that the CSV data has the required columns and valid values
 */
function validateCsvData(data) {
  const requiredColumns = ["type", "url", "top", "center", "bottom"];

  if (!data || data.length === 0) {
    return { valid: false, message: "CSV data is empty" };
  }

  // Check if all required columns exist
  const missingColumns = requiredColumns.filter((col) => !(col in data[0]));
  if (missingColumns.length > 0) {
    return {
      valid: false,
      message: `Missing required columns: ${missingColumns.join(", ")}`,
    };
  }

  // Check required fields are not empty (center can be empty)
  for (let idx = 0; idx < data.length; idx++) {
    const row = data[idx];
    if (!String(row.type || "").trim()) {
      return {
        valid: false,
        message: `Type column cannot contain empty values (row ${idx + 1})`,
      };
    }
    if (!String(row.url || "").trim()) {
      return {
        valid: false,
        message: `URL column cannot contain empty values (row ${idx + 1})`,
      };
    }
    if (!String(row.top || "").trim()) {
      return {
        valid: false,
        message: `Top column cannot contain empty values (row ${idx + 1})`,
      };
    }
    if (!String(row.bottom || "").trim()) {
      return {
        valid: false,
        message: `Bottom column cannot contain empty values (row ${idx + 1})`,
      };
    }
  }

  return { valid: true, message: "CSV data is valid" };
}

/**
 * Reset the CSV upload section to initial state
 */
function resetCsvUpload() {
  // Reset the file input
  document.getElementById("csv-file").value = "";
  csvData = null;

  // Hide success state and show upload prompt
  document.getElementById("csv-upload-success").classList.add("hidden");
  document.getElementById("csv-upload-prompt").classList.remove("hidden");
}

/**
 * Update the upload UI to show the uploaded filename
 */
function updateUploadUI(filename) {
  document.getElementById("csv-filename").textContent = filename;
  document.getElementById("csv-upload-prompt").classList.add("hidden");
  document.getElementById("csv-upload-success").classList.remove("hidden");
}

/**
 * Load and validate the CSV file
 */
async function loadCsvFile(event) {
  const fileList = event.target.files;
  if (!fileList.length) {
    return;
  }

  const file = fileList[0];

  try {
    // Use PapaParse to parse the CSV file
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: function (results) {
        // Filter out completely empty rows
        csvData = results.data.filter((row) =>
          Object.values(row).some((v) => (v || "").trim()),
        );

        // Validate the CSV data
        const validation = validateCsvData(csvData);
        if (!validation.valid) {
          showError(`CSV validation failed: ${validation.message}`);
          csvData = null;
          return;
        }

        // Get unique card types (excluding 'back' if present)
        const uniqueTypes = [
          ...new Set(
            csvData.map((row) => row.type).filter((type) => type !== "back"),
          ),
        ];

        // Update the upload UI with the filename
        updateUploadUI(file.name);

        // Generate color pickers for each type
        generateCardTypeColors(uniqueTypes);

        showSuccess(
          `CSV file loaded successfully! Found ${csvData.length} cards with ${uniqueTypes.length} unique type(s): ${uniqueTypes.sort().join(", ")}.`,
        );
      },
      error: function (error) {
        showError(
          `Error reading CSV file: ${error.message}. Please ensure your file is in CSV format.`,
        );
        // Reset the input value to allow re-upload
        resetCsvUpload();
      },
    });
  } catch (e) {
    showError(
      `Error reading CSV file: ${e.message}. Please ensure your file is in CSV format.`,
    );
    // Reset the input and UI
    resetCsvUpload();
  }
}

/**
 * Create the front of a card
 */
function createCardFront(record, pdf, config, x, y) {
  const CARD_SIZE = config.CARD_SIZE;
  const COLOR = config.CARD_COLORS[record.type];

  // Draw background
  const bgColor = rgbFromHex(COLOR.bg);
  pdf.setFillColor(bgColor.r, bgColor.g, bgColor.b);
  pdf.rect(x, y, CARD_SIZE, CARD_SIZE, "F");

  // Set text color
  const textColor = rgbFromHex(COLOR.text);
  pdf.setTextColor(textColor.r, textColor.g, textColor.b);

  // Place the center in the center of the card
  if (String(record.center || "").trim()) {
    const centerText = String(record.center);
    const maxWidth = CARD_SIZE - 8; // keep small side padding
    const baseSize = 48;
    const minSize = 14;

    pdf.setFont("helvetica", "bold");
    pdf.setFontSize(baseSize);

    const baseWidth = pdf.getTextWidth(centerText);
    const scale = Math.min(1, maxWidth / baseWidth);
    const finalSize = Math.max(minSize, Math.floor(baseSize * scale));

    pdf.setFontSize(finalSize);
    pdf.text(centerText, x + CARD_SIZE / 2, y + CARD_SIZE / 2, {
      align: "center",
      baseline: "middle",
    });
  }

  // Place the top text above the center
  pdf.setFontSize(14);
  pdf.setFont("helvetica", "bold");
  const topLines = pdf.splitTextToSize(record.top, CARD_SIZE - 4);
  // Calculate line height and adjust position to center multi-line text
  const topLineHeight = pdf.getLineHeight() / pdf.internal.scaleFactor;
  const topOffset = ((topLines.length - 1) * topLineHeight) / 2;
  pdf.text(topLines, x + CARD_SIZE / 2, y + 14 - topOffset, {
    align: "center",
  });

  // Place the bottom text below the center
  if (String(record.bottom || "").trim()) {
    pdf.setFont("helvetica", "italic");
    const bottomLines = pdf.splitTextToSize(record.bottom, CARD_SIZE - 4);
    // Calculate line height and adjust position to center multi-line text
    const bottomLineHeight = pdf.getLineHeight() / pdf.internal.scaleFactor;
    const bottomOffset = ((bottomLines.length - 1) * bottomLineHeight) / 2;
    pdf.text(
      bottomLines,
      x + CARD_SIZE / 2,
      y + CARD_SIZE - 10 - bottomOffset,
      {
        align: "center",
      },
    );
  }
}

/**
 * Create the back of a card with QR code
 */
async function createCardBack(record, pdf, config, x, y) {
  const CARD_SIZE = config.CARD_SIZE;
  const COLOR = config.CARD_COLORS.back;

  // Draw background
  const bgColor = rgbFromHex(COLOR.bg);
  pdf.setFillColor(bgColor.r, bgColor.g, bgColor.b);
  pdf.rect(x, y, CARD_SIZE, CARD_SIZE, "F");

  // Generate QR code using QRious
  const textColor = rgbFromHex(COLOR.text);
  const qr = new QRious({
    value: record.url,
    size: 500, // High resolution for quality
    foreground: `rgb(${textColor.r}, ${textColor.g}, ${textColor.b})`,
    background: `rgb(${bgColor.r}, ${bgColor.g}, ${bgColor.b})`,
    level: "L",
  });

  // Add QR code to PDF
  const qrDataUrl = qr.toDataURL("image/jpeg", 0.85);
  pdf.addImage(qrDataUrl, "JPEG", x + 8, y + 8, CARD_SIZE - 16, CARD_SIZE - 16);
}

/**
 * Create PDF with all cards
 */
async function createPdfBytes(data, config) {
  const PAPER_WIDTH = config.PAPER_WIDTH;
  const PAPER_HEIGHT = config.PAPER_HEIGHT;
  const BLEED = config.BLEED;
  const CARD_SIZE = config.CARD_SIZE;
  const GAP = config.GAP;
  const CARD_MARGIN = config.CARD_MARGIN;

  // Create PDF with custom page size
  const { jsPDF } = window.jspdf;
  const pdf = new jsPDF({
    orientation: "portrait",
    unit: "mm",
    format: [PAPER_WIDTH + 2 * BLEED, PAPER_HEIGHT + 2 * BLEED],
  });

  pdf.setFont("helvetica");

  // Calculate the number of columns and rows that fit on the page
  const nColumns = Math.floor(
    (PAPER_WIDTH - 2 * CARD_MARGIN + GAP) / (CARD_SIZE + GAP),
  );
  const nRowsPerPage = Math.floor(
    (PAPER_HEIGHT - 2 * CARD_MARGIN + GAP) / (CARD_SIZE + GAP),
  );
  const nRows = Math.ceil(data.length / nColumns);

  // Calculate the number of pages needed
  const nPages = Math.ceil(nRows / nRowsPerPage);

  for (let page = 0; page < nPages; page++) {
    // Get the cards for this page
    const startIdx = page * nRowsPerPage * nColumns;
    const endIdx = (page + 1) * nRowsPerPage * nColumns;
    const cardsOnPage = data.slice(startIdx, endIdx);

    // Add page for fronts
    if (page > 0) pdf.addPage();

    // Create the front of the cards, starting at the top left corner of the page
    for (let i = 0; i < nColumns; i++) {
      for (let j = 0; j < nRowsPerPage; j++) {
        const idx = i + j * nColumns;
        if (idx >= cardsOnPage.length) break;

        const record = cardsOnPage[idx];
        const cardX = BLEED + CARD_MARGIN + i * (CARD_SIZE + GAP);
        const cardY = BLEED + CARD_MARGIN + j * (CARD_SIZE + GAP);
        createCardFront(record, pdf, config, cardX, cardY);
      }
    }

    // Add page for backs
    pdf.addPage();

    // Create the back of the cards, starting at the top right corner of the page
    // This is necessary for double-sided printing
    for (let i = nColumns - 1; i >= 0; i--) {
      for (let j = 0; j < nRowsPerPage; j++) {
        const idx = i + j * nColumns;
        if (idx >= cardsOnPage.length) break;

        const record = cardsOnPage[idx];
        const cardX =
          BLEED + CARD_MARGIN + (nColumns - 1 - i) * (CARD_SIZE + GAP);
        const cardY = BLEED + CARD_MARGIN + j * (CARD_SIZE + GAP);
        await createCardBack(record, pdf, config, cardX, cardY);
      }
    }
  }

  return pdf;
}

/**
 * Collect configuration from the form inputs
 */
function collectConfig() {
  const config = {};

  // Numeric configuration
  config.PAPER_WIDTH = parseFloat(document.getElementById("paper-width").value);
  config.PAPER_HEIGHT = parseFloat(
    document.getElementById("paper-height").value,
  );
  config.BLEED = parseFloat(document.getElementById("bleed").value);
  config.CARD_SIZE = parseFloat(document.getElementById("card-size").value);
  config.GAP = parseFloat(document.getElementById("gap").value);
  config.CARD_MARGIN = parseFloat(document.getElementById("card-margin").value);

  // Color configuration - always include back
  config.CARD_COLORS = {
    back: {
      bg: document.getElementById("back-bg").value,
      text: document.getElementById("back-text").value,
    },
  };

  // Dynamically collect colors for card types found in CSV
  if (csvData !== null) {
    const uniqueTypes = [
      ...new Set(
        csvData.map((row) => row.type).filter((type) => type !== "back"),
      ),
    ];
    uniqueTypes.forEach((cardType) => {
      const bgInput = document.getElementById(`${cardType}-bg`);
      const textInput = document.getElementById(`${cardType}-text`);
      if (bgInput && textInput) {
        config.CARD_COLORS[cardType] = {
          bg: bgInput.value,
          text: textInput.value,
        };
      }
    });
  }

  return config;
}

/**
 * Generate the PDF from the loaded CSV data and configuration
 */
async function generatePDF(event) {
  // Check if CSV data is loaded
  if (csvData === null) {
    showError("Please upload a CSV file first.");
    return;
  }

  // Collect configuration
  let config;
  try {
    config = collectConfig();
  } catch (e) {
    showError(`Error reading configuration: ${e.message}`);
    return;
  }

  // Generate PDF
  try {
    // Disable button during generation
    const btn = document.getElementById("generate-btn");
    btn.disabled = true;

    showStatus("Generating PDF... This may take a moment.");
    await yieldToBrowser();

    const pdf = await createPdfBytes(csvData, config);

    // Save the PDF
    pdf.save("cards.pdf");

    showSuccess(
      "PDF generated successfully! Your download should start automatically.",
    );

    // Re-enable button
    btn.disabled = false;
  } catch (e) {
    showError(`Error generating PDF: ${e.message}`);
    console.error("PDF generation error:", e);
    // Re-enable button
    document.getElementById("generate-btn").disabled = false;
  }
}

// Set up event listeners when DOM is ready
document.addEventListener("DOMContentLoaded", function () {
  const fileInput = document.getElementById("csv-file");
  if (fileInput) {
    fileInput.addEventListener("change", loadCsvFile);
  }

  // Make generatePDF available globally
  window.generatePDF = generatePDF;
});

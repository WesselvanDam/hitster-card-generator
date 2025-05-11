import os
import math
from fpdf import FPDF
import pandas as pd
import qrcode

from .config import *


def create_card_front(record: pd.Series, pdf: FPDF):
  """Creates a square card with the record data.

  The card has a color based on the type of the record.

  The card shows the 'center' text in a large font in the center of the card.
  Above is the 'top' text and below is the 'bottom' text, both in smaller fonts.
  """
  COLOR = CARD_COLORS[record["type"]]
  card_x = pdf.get_x()
  card_y = pdf.get_y()
  pdf.set_fill_color(*COLOR["bg"])
  pdf.rect(pdf.get_x(), pdf.get_y(), CARD_SIZE, CARD_SIZE, style="F")
  pdf.set_fill_color(255, 255, 255)

  # Place the center in the center of the card
  if not pd.isna(record["center"]):
    pdf.set_text_color(*COLOR["text"])
    pdf.set_font(size=48, style="B")
    pdf.set_xy(card_x + (CARD_SIZE / 2), card_y + CARD_SIZE / 2 - pdf.font_size / 2)
    pdf.cell(CARD_SIZE, None, str(record["center"]), align="X")

  # Place the top text above the center
  pdf.set_font(size=14, style="B")
  pdf.set_xy(card_x + (CARD_SIZE / 2), card_y + 6)
  pdf.multi_cell(CARD_SIZE - 4, None, record["top"], align="X")

  # Place the bottom text below the center
  if not pd.isna(record["bottom"]):
    pdf.set_font(style="I")
    pdf.set_xy(card_x + (CARD_SIZE / 2), card_y + CARD_SIZE - 14)
    pdf.multi_cell(CARD_SIZE - 4, None, record["bottom"], align="X")


def create_card_back(record: pd.Series, pdf: FPDF):
  """Creates a square card showing a QR code of the 'url' property of the record."""
  COLOR = CARD_COLORS["back"]
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

  # Store the QR code in a temporary file located in outputs/tmp/
  os.makedirs("outputs/tmp", exist_ok=True)
  tmp_file = f"{record['top']}_{record['bottom']}"
  # Filter out invalid characters for the filename
  tmp_file = "".join(c for c in tmp_file if c.isalnum() or c in ("_", "-"))
  img.save(f"outputs/tmp/{tmp_file}.png")

  pdf.image(
    f"outputs/tmp/{tmp_file}.png",
    card_x + 1,
    card_y + 1,
    CARD_SIZE - 1,
    CARD_SIZE - 1,
  )

  # Remove the temporary file
  os.remove(f"outputs/tmp/{tmp_file}.png")


def create_pdf(data: pd.DataFrame):
  """Creates a PDF with the data from the DataFrame.

  The PDF contains a grid of cards, each card representing a record in the data.

  The grids has three columns and as many rows as fit on the page. If more rows are needed, a new page is added.
  """
  pdf = FPDF(format=[PAPER_WIDTH + 2 * BLEED, PAPER_HEIGHT + 2 * BLEED], unit="mm")
  pdf.set_font("Helvetica", size=12)
  pdf.set_margins(
    BLEED + CARD_MARGIN,
    BLEED + CARD_MARGIN,
    BLEED + CARD_MARGIN,
  )

  # Calculate the number of columns and rows that fit on the page.
  n_columns = (PAPER_WIDTH - 2 * CARD_MARGIN + GAP) // (CARD_SIZE + GAP)
  n_rows_per_page = (PAPER_HEIGHT - 2 * CARD_MARGIN + GAP) // (CARD_SIZE + GAP)
  n_rows = len(data) // n_columns + 1

  # Calculate the number of pages needed.
  n_pages = math.ceil(n_rows / n_rows_per_page)

  for page in range(n_pages):
    # Get the cards for this page.
    cards_on_page = data[
      page * n_rows_per_page * n_columns : (page + 1) * n_rows_per_page * n_columns
    ]
    pdf.add_page()

    # Create the front of the cards, starting at the top left corner of the page
    for i in range(n_columns):
      row_x = pdf.get_x()
      row_y = pdf.get_y()
      for j in range(n_rows_per_page):
        idx = i + j * n_columns
        if idx >= len(cards_on_page):
          break
        record = cards_on_page.iloc[idx]
        # Set the position of the card
        pdf.set_xy(row_x, row_y + j * CARD_SIZE + j * GAP)
        create_card_front(record, pdf)
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
        record = cards_on_page.iloc[idx]
        # Set the position of the card
        pdf.set_xy(row_x, row_y + j * CARD_SIZE + j * GAP)
        create_card_back(record, pdf)
      # Set the position for the next row
      pdf.set_xy(row_x + CARD_SIZE + GAP, row_y)

  # Add two pages with /data/token.png tokens at the end.
  pdf.add_page()
  # Start at the top left corner of the page, but with a margin of TOKEN_GAP.
  pdf.set_xy(BLEED + TOKEN_MARGIN, BLEED + TOKEN_MARGIN)

  # Create rows of tokens. Calculate how many tokens fit in a row.

  n_tokens_per_row = round((PAPER_WIDTH - 2 * TOKEN_MARGIN + GAP) / (TOKEN_SIZE + TOKEN_GAP))
  n_tokens_per_col = round((PAPER_HEIGHT - 2 * TOKEN_MARGIN + GAP) / (TOKEN_SIZE + TOKEN_GAP))
  for row in range(n_tokens_per_col):
    for col in range(n_tokens_per_row):
      pdf.image(
        "assets/token.png",
        pdf.get_x() + col * (TOKEN_SIZE + TOKEN_GAP),
        pdf.get_y() + row * (TOKEN_SIZE + TOKEN_GAP),
        TOKEN_SIZE,
      )
  pdf.add_page()

  pdf.set_xy(BLEED + TOKEN_MARGIN, BLEED + TOKEN_MARGIN)
  for row in range(n_tokens_per_col):
    for col in range(n_tokens_per_row):
      pdf.image(
        "assets/token.png",
        pdf.get_x() + col * (TOKEN_SIZE + TOKEN_GAP),
        pdf.get_y() + row * (TOKEN_SIZE + TOKEN_GAP),
        TOKEN_SIZE,
      )

  pdf.output("outputs/output.pdf")
  print(f"PDF created successfully at {os.path.abspath('outputs/output.pdf')}")

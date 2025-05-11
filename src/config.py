"""
This file contains the configuration for the cards.

Constants used for card and token configuration:
- BLEED: The page bleed area (in millimeters) outside the page that is cut off during printing.
         Print companies usually state what the bleed area should be.
- CARD_SIZE: The size of a card (in millimeters).
- GAP: The gap between cards (in millimeters).
- CARD_MARGIN: The margin around a card (in millimeters).
- TOKEN_SIZE: The size of a token (in millimeters).
- TOKEN_GAP: The gap between tokens (in millimeters).
- TOKEN_MARGIN: The margin around a token (in millimeters).
- CARD_COLORS: A dictionary defining the background and text colors for different card types.
  - "back": Colors for the back of the card.
  - "song": Colors for song cards.
  - "video": Colors for video cards.
  - "article": Colors for article cards.
  - "painting": Colors for painting cards.
"""

def _check_size(bleed, size, gap, margin):
  """Check if the size of the card is valid."""
  assert bleed >= 0, "Bleed must be greater than or equal to 0"
  assert size > 0, "Size must be greater than 0"
  assert gap > 0, "Gap must be greater than 0"
  assert margin > 0, "Margin must be greater than 0"
  assert (PAPER_WIDTH - 2 * margin + gap) % (size + gap) == 0, f"""
  Invalid card configuration: the card size and gap should fit perfectly in the width of the page, minus the bleed and margin. Note that the gap is the space between two cards, and therefore there is one less gap than cards.

  For A4 paper, the recommended configuration is:
  \tcard size: 66mm
  \tcard gap: 3mm
  \tcard margin: 3mm
  \ttoken size: 28mm
  \ttoken gap: 6mm
  \ttoken margin: 6mm
  """


PAPER_WIDTH = 210
PAPER_HEIGHT = 297

BLEED =  3

CARD_SIZE = 66
GAP = 3
CARD_MARGIN = 3
_check_size(BLEED, CARD_SIZE, GAP, CARD_MARGIN)


TOKEN_SIZE = 28
TOKEN_GAP = 6
TOKEN_MARGIN = 6
_check_size(BLEED, TOKEN_SIZE, TOKEN_GAP, TOKEN_MARGIN)

CARD_COLORS = {
  "back": {
      "bg": (172, 200, 229),
      "text": (17, 42, 70),
  },
  "song": {
      "bg": (140, 190, 178),
      "text": (25, 38, 35),
  },
  "video": {
      "bg": (243, 181, 98),
      "text": (51, 35, 14),
  },
  "article": {
      "bg": (240, 96, 96),
      "text": (50, 14, 14),
  },
  "painting": {
      "bg": (242, 235, 191),
      "text": (51, 49, 38),
  },
}

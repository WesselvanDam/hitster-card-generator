import os
import pandas as pd

from src.pdf import create_pdf


def main():
  files = [file for file in os.listdir("data") if file.endswith(".csv")]

  if len(files) == 0:
    print("No files found in the data directory. Please put a csv file in the data directory.")
    return
  elif len(files) == 1:
    choice = 1
  else:
    while True:
      print("\nChoose a file to parse:")
      for i, file in enumerate(files):
        print(f"\t{i+1}: {file}")
      choice = input("Enter a number: ")
      try:
        choice = int(choice)
        if 1 <= choice <= len(files):
          break
        else:
          print("Invalid choice. Try again.")
      except ValueError:
        print("Invalid choice. Try again.")

  filename = files[choice - 1]
  data = pd.read_csv(f"data/{filename}", sep=None, engine="python")
  print(f"Parsing {filename}:\n")
  print(data.to_string(index=False, max_colwidth=30))
  print(f"\nNumber of cards: {len(data)}")

  create_pdf(data)
  

if __name__ == "__main__":
  main()
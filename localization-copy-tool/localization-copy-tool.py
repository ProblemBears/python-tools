import os
import pandas as pd
import polib

# Define base directory for translations (mounted folder)
TRANSLATIONS_DIR = "translations"  # This is the volume folder

# Construct file paths for the Excel and PO files
xlsx_file = os.path.join(TRANSLATIONS_DIR, "Spanish.xlsx")  # Replace with your actual file name
po_file = os.path.join(TRANSLATIONS_DIR, "Game.po")  # Replace with your actual file name

# Load the Excel file with multiple sheets
sheets = pd.read_excel(xlsx_file, sheet_name=None)  # Load all sheets as a dictionary

# Load the PO file
po = polib.pofile(po_file)

unfound_dictionary = {}

# Loop through each sheet (language)
for sheet_name, df in sheets.items():
    ## Log the current sheet's name
    print(f"Processing sheet: {sheet_name}")
    
    # Print out the columns to see if any invisible characters or extra spaces exist
    print("Columns in this sheet:", df.columns.tolist())
    # Strip the column names from extra spaces or formatting
    df.columns = df.columns.str.strip()  # Remove leading/trailing spaces
    try:
        # Find the index of the column that contains the header "Full Text"
        source_text_index = df.columns.get_loc("Full Text")
        translation_text_index = df.columns.get_loc("Language")
        print(f"Found 'Full Text' column at index: {source_text_index}")
    except KeyError:
        print("Column 'Full Text' or 'Language' not found in this sheet.")
        continue

    # Iterate over each row in the sheet
    for index, row in df.iterrows():
        # Log the row and store source & translation text to variables
        source_text = row[source_text_index]
        translation_text = row[translation_text_index]
        print(f"Row ({index}) - Source : {source_text} - Translation : {translation_text}")

        # Check if the value is NaN and skip this iteration if so
        if pd.isna(source_text):
            print(f"Skipping row {index} due to NaN value")
            continue

        # Find and update the matching entry in the .po file
        for entry in po:
            if entry.msgid == source_text:
                print("Source Text found in .po file. Added new Translation")
                entry.msgstr = translation_text

# Save the updated PO file to the translations folder
output_po_file = os.path.join(TRANSLATIONS_DIR, "Game_Translated.po")  # Naming convention for output
po.save(output_po_file)
print(f"Saved updated PO file: {output_po_file}")

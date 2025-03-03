import os
import pandas as pd
import polib
from collections import defaultdict

TRANSLATIONS_DIR = "translations"  # Directory where inputs are place AND output .pos are generated
REPORTS_DIR = "reports"  # Output directory for reports

######################################################################################################################################################################################################
def translate_po_file():
    """Runs the existing translation logic"""
    # Detect the first .xlsx file in the translations folder
    xlsx_files = [f for f in os.listdir(TRANSLATIONS_DIR) if f.endswith(".xlsx")]
    if not xlsx_files:
        print("Error: No .xlsx file found in the translations directory!")
        return
    xlsx_file = os.path.join(TRANSLATIONS_DIR, xlsx_files[0])  # Use the first found file
    print(f"Using translation file: {xlsx_file}")

    po_file = os.path.join(TRANSLATIONS_DIR, "Game.po")
    # Ensure the .po file exists
    if not os.path.exists(po_file):
        print(f"Error: PO file '{po_file}' not found!")
        return

    # Load Excel file & Game.p
    sheets = pd.read_excel(xlsx_file, sheet_name=None)
    po = polib.pofile(po_file)

    missing_sources = []  # Store missing sources of .po
    missing_translations = [] # Store missing translations

    for sheet_name, df in sheets.items():
        print(f"Processing sheet: {sheet_name}")
        df.columns = df.columns.astype(str).str.strip() # Clean column names

        try:
            source_text_index = df.columns.get_loc("Full Text")
            translation_text_index = df.columns.get_loc("Language")
        except KeyError:
            print("Column 'Full Text' or 'Language' not found.")
            continue

        for index, row in df.iterrows():
            source_text = row.iloc[source_text_index]
            translation_text = row.iloc[translation_text_index]

            if pd.isna(source_text):
                continue

            found = False  # Track if source_text exists in the .po file
            for entry in po:
                if entry.msgid == source_text:
                    found = True
                    if pd.isna(translation_text):
                        missing_translations.append((sheet_name, source_text))
                        continue
                    entry.msgstr = translation_text

            if not found:
                missing_sources.append((sheet_name, source_text, index+2))

    # Save updated .po file
    output_po_file = os.path.join(TRANSLATIONS_DIR, "Game_Translated.po")
    po.save(output_po_file)
    print(f"Saved updated PO file: {output_po_file}")

    # Generate source missing report
    if missing_sources:
        os.makedirs(REPORTS_DIR, exist_ok=True)  # Ensure reports directory exists
        missing_sources_report_file = os.path.join(REPORTS_DIR, "missing_sources_report.txt")

        with open(missing_sources_report_file, "w", encoding="utf-8") as file:
            file.write("These entries were detected in the .xlsx BUT they couldn't be found in the .po - It's possible they haven't been added to the game:\n\n")
            for sheet, text, index in missing_sources:
                file.write(f"------------------------\n")
                file.write(f"Sheet: {sheet}\nRow (i): {index}\nMissing Source Text:\n{text}\n")
                file.write(f"------------------------\n\n")

        print(f"Missing translations report saved to '{missing_sources_report_file}'")
    else:
        print("No missing translations found.")

    # Generate translation missing report
    if missing_translations:
        os.makedirs(REPORTS_DIR, exist_ok=True)  # Ensure reports directory exists
        missing_translations_report_file = os.path.join(REPORTS_DIR, "missing_translations_report.txt")

        with open(missing_translations_report_file, "w", encoding="utf-8") as file:
            file.write("These entries were detected in the .xlsx AND were found in the .po - BUT their translations are missing:\n\n")
            for sheet, source_text in missing_translations:
                file.write(f"------------------------\n")
                file.write(f"Sheet: {sheet}\nFound Source Text:\n{source_text}\nMissing Translation Text:\nNaN\n")
                file.write(f"------------------------\n\n")

        print(f"Missing translations report saved to '{missing_translations_report_file}'")
    else:
        print("No missing translations found.")

#######################################################################################################################################################################################################
def delete_all_translations():
    """(Future) Deletes all translations from .po file"""

    po_file = os.path.join(TRANSLATIONS_DIR, "Game.po")
    # Ensure the .po file exists
    if not os.path.exists(po_file):
        print(f"Error: PO file '{po_file}' not found!")
        return
    po = polib.pofile(po_file)

    # Iterate through each entry and clear the translation field
    for entry in po:
        entry.msgstr = ""  # Clear the translation

    # Save the updated .po file
    po.save(po_file)
    print(f"All translations cleared and '{po_file}' overwritten.")

########################################################################################################################################################################################################
def detect_duplicate_source_text():
    po_file = os.path.join(TRANSLATIONS_DIR, "Game.po")

    if not os.path.exists(po_file):
        print(f"Error: PO file '{po_file}' not found!")
        return

    po = polib.pofile(po_file)

    # Dictionary to track occurrences of each msgid
    msgid_counts = defaultdict(int)

    # Count occurrences of each source text (msgid)
    for entry in po:
        msgid_counts[entry.msgid] += 1

    # Filter only duplicates (msgid that appear more than once)
    duplicates = {msgid: count for msgid, count in msgid_counts.items() if count > 1}

    if not duplicates:
        print("No duplicate source text entries found.")
        return

    # Ensure 'reports' directory exists
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # Save duplicates to a text file inside 'reports' directory
    report_filepath = os.path.join(REPORTS_DIR, "duplicates_report.txt")
    with open(report_filepath, "w", encoding="utf-8") as file:
        file.write("Duplicate Source Text Entries:\n\n")
        for msgid, count in duplicates.items():
            file.write(f"Occurrences: {count}\nText: {msgid}\n\n")

    print(f"Duplicate report saved to '{report_filepath}'")

########################################################################################################################################################################################################
def delete_all_files():
    """Deletes all files inside the 'reports' and 'translations' directories."""
    for directory in [REPORTS_DIR, TRANSLATIONS_DIR]:
        if os.path.exists(directory):
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
    
    print(f"All files inside '{REPORTS_DIR}' and '{TRANSLATIONS_DIR}' have been deleted.")

# --- INTERACTIVE MENU --- ###############################################################################################################################################################
while True:
    print("\nType a number of the corresponding command, then press Enter to run the command :")
    print("0 - Generate a new Game_Translated.po - By copying translations from a given .xlsx to a given Game.po - Generates a report of missing Source Text in the .po")
    print("1 - Delete All Translations from a given Game.po")
    print("2 - Generate Summary of Duplicates in a Game.po")
    print("d - Delete ALL files inside 'reports' and 'translations' folders")

    print("q - Quit")

    choice = input("Enter your choice: ").strip()

    if choice == "0":
        translate_po_file()
    elif choice == "1":
        delete_all_translations()
    elif choice == "2":
        detect_duplicate_source_text()
    elif choice.lower() == "d":
        delete_all_files()

    elif choice.lower() == "q":
        print("Exiting...")
        break
    else:
        print("Invalid choice. Please enter 0, 1, 2, or q.")

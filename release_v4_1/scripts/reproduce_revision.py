"""Rebuild reporting additions and text; --word also regenerates editable DOCX files.
This command does not refit either BCI decoder or rerun the factorial/power studies.
"""
from pathlib import Path
import argparse,subprocess,sys
p=argparse.ArgumentParser();p.add_argument("--word",action="store_true");a=p.parse_args()
s=Path(__file__).resolve().parent
for name in ["recover_reporting.py","build_text.py","build_response.py"]+(["build_word_documents.py"] if a.word else []):
    subprocess.run([sys.executable,str(s/name)],check=True)
print("Revision reporting reconstructed. Regenerated DOCX files require visual review before submission.")

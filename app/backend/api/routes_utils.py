import sys
import subprocess
import tkinter as tk
from tkinter import filedialog
from fastapi import APIRouter

router = APIRouter(prefix="/api/utils", tags=["utils"])

@router.get("/pick-file")
def pick_file() -> dict:
    """
    Opens a file dialog in a separate process to avoid blocking the asyncio loop
    or crashing due to thread safety issues with Tkinter.
    """
    script = """
import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.withdraw()
root.wm_attributes('-topmost', 1)
file_path = filedialog.askopenfilename(
    title="Selecciona un video",
    filetypes=[("Video files", "*.mp4 *.mov *.avi *.mkv *.webm"), ("All files", "*.*")]
)
print(file_path, end="")
"""
    try:
        # Run the script in a separate process
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            check=True
        )
        file_path = result.stdout
        return {"path": file_path}
    except Exception as e:
        print(f"Error opening file dialog: {e}")
        return {"path": ""}

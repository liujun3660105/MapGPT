from pathlib import Path 
import os
from metagpt.logs import logger
import mapagent

def get_root_path():
    """Get the root directory of the installed package."""
    package_root = Path(mapagent.__file__).parent.parent
    for i in (".git", ".project_root", ".gitignore"):
        if (package_root / i).exists():
            break
    else:
        package_root = Path.cwd()

    logger.info(f"Package root set to {str(package_root)}")
    return package_root

METAGPT_ROOT = get_root_path() 
DATA_PATH = METAGPT_ROOT / "data"
TUTORIAL_PATH = DATA_PATH / "tutorial_docx"
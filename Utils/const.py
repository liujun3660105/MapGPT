from pathlib import Path 
import os
from metagpt.logs import logger
import MapAgent

def get_metagpt_package_root():
    """Get the root directory of the installed package."""
    package_root = Path(MapAgent.__file__).parent.parent
    for i in (".git", ".project_root", ".gitignore"):
        if (package_root / i).exists():
            break
    else:
        package_root = Path.cwd()

    logger.info(f"Package root set to {str(package_root)}")
    return package_root


def get_metagpt_root():
    """Get the project root directory."""
    # Check if a project root is specified in the environment variable
    project_root_env = os.getenv("METAGPT_PROJECT_ROOT")
    if project_root_env:
        project_root = Path(project_root_env)
        logger.info(f"PROJECT_ROOT set from environment variable to {str(project_root)}")
    else:
        # Fallback to package root if no environment variable is set
        project_root = get_metagpt_package_root()
    return project_root

METAGPT_ROOT = get_metagpt_root() 
DATA_PATH = METAGPT_ROOT / "data"
TUTORIAL_PATH = DATA_PATH / "tutorial_docx"
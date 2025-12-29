"""
AgentClick V2 - Module Entry Point

This module enables executing AgentClick V2 as a Python module:
    python -m agentclick_v2

It delegates to the main.py entry point in the project root.

Story: 0-Integration & Bootstrap (AC: #8)
"""

import sys
from pathlib import Path

# Add project root to path so we can import main
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import and run main
if __name__ == "__main__":
    import main
    main.main()

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.infrastructure.models.deal_model import Base
target_metadata = Base.metadata

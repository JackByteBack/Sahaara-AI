import os
import sys
from pathlib import Path

# Configure a hermetic test database BEFORE the app is imported
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["DATABASE_URL"] = "sqlite:///./test_sahaara.db"
os.environ["SEED_DEMO_USERS"] = "true"
os.environ["OPENAI_API_KEY"] = ""

TEST_DB = Path(__file__).resolve().parents[1] / "test_sahaara.db"
if TEST_DB.exists():
    TEST_DB.unlink()

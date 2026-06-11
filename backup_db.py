import shutil
import datetime

data = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

shutil.copy(
    "players.db",
    f"backup_{data}.db"
)

print("Backup criado.")
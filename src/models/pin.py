from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class PinMetadata:
    pin_url: str
    image_url: Optional[str] = None
    filename: Optional[str] = None
    status: str = "pending"

    def to_dict(self) -> dict:
        """Метод для конвертации объекта в словарь (пригодится для сохранения в CSV)."""
        return asdict(self)

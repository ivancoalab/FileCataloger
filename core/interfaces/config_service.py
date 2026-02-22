from abc import ABC, abstractmethod
from typing import Dict


class IConfigService(ABC):

    @abstractmethod
    def load(self) -> Dict:
        pass

    @abstractmethod
    def save(self, config: Dict) -> None:
        pass

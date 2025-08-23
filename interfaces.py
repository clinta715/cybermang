from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

class IPlayer(ABC):
    @property
    @abstractmethod
    def x(self) -> int:
        pass

    @property
    @abstractmethod
    def y(self) -> int:
        pass

    @property
    @abstractmethod
    def health(self) -> int:
        pass

    @abstractmethod
    def move(self, dx: int, dy: int, game_map: 'IMap', weapons: List['IWeapon']) -> None:
        pass

    @abstractmethod
    def take_damage(self, damage: int) -> None:
        pass

class IEnemy(ABC):
    @property
    @abstractmethod
    def x(self) -> int:
        pass

    @property
    @abstractmethod
    def y(self) -> int:
        pass

    @property
    @abstractmethod
    def health(self) -> int:
        pass

    @abstractmethod
    def move_towards(self, target_x: int, target_y: int, game_map: 'IMap') -> None:
        pass

    @abstractmethod
    def check_collision(self, player: IPlayer) -> bool:
        pass

    @abstractmethod
    def take_damage(self, damage: int) -> None:
        pass

class IMap(ABC):
    @property
    @abstractmethod
    def width(self) -> int:
        pass

    @property
    @abstractmethod
    def height(self) -> int:
        pass

    @abstractmethod
    def render(self, stdscr, colors: bool = False) -> None:
        pass

    @abstractmethod
    def is_blocked(self, x: int, y: int) -> bool:
        pass

    @abstractmethod
    def get_terrain_effect(self, x: int, y: int) -> float:
        pass

    @abstractmethod
    def collect_item(self, x: int, y: int) -> Optional[str]:
        pass

class IGame(ABC):
    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def handle_input(self, key: int) -> None:
        pass

    @abstractmethod
    def update(self) -> None:
        pass

    @abstractmethod
    def render(self) -> None:
        pass

class IWeapon(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def ammo(self) -> int:
        pass

    @property
    @abstractmethod
    def ammo_capacity(self) -> int:
        pass

    @abstractmethod
    def shoot(self, x: int, y: int, direction: str, game_map: IMap, enemies: List[IEnemy], stdscr) -> bool:
        pass

    @abstractmethod
    def reload(self, amount: int) -> None:
        pass
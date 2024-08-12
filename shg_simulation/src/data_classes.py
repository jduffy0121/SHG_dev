import types
import pathlib
from dataclasses import dataclass, field
from typing import List, Tuple, Dict
from matplotlib import figure, axes

@dataclass
class PointGroupFit:
    name: str = ''
    channel: str = ''
    func: types.FunctionType = field(default_factory=lambda x: x)
    weights: List[Tuple[str, float]] = field(default_factory=lambda: [()])
    fit_r: List[float] = field(default_factory=lambda: [0.0])
    fit_phi: List[float] = field(default_factory=lambda: [0.0])
    r2: float = 1.0
    legend: str = ''
    active: bool = False

@dataclass
class FitManager:
    point_groups: List[PointGroupFit] = field(default_factory=lambda: [])
    selection_mode: str = 'Single'
    selected_channels: List[str] = field(default_factory=lambda: [])
    plots_showing: List[str] = field(default_factory=lambda: [])
    prev_selected: List[str] = field(default_factory=lambda: [])
    expanded_window: bool = False
    figures: List[Tuple[figure, axes]] = field(default_factory=lambda: [])
    data_color: str = 'blue'

@dataclass
class FitConfig:
    geometry: str = ''
    channels: List[str] = field(default_factory=lambda: [])
    data: Dict[str, List[float]] = field(default_factory=lambda: {})
    data_files: List[pathlib.Path] = field(default_factory=lambda: [None] * 6)
    column_headers: bool = False
    source: str = ''
    sys: str = ''
    plane: str = ''

@dataclass
class FitInputManager:
    valid_channels: List[str] = field(default_factory=lambda: [])
    data_files: List[pathlib.Path] = field(default_factory=lambda: [None] * 6)
    column_headers: bool = False

@dataclass
class SimInputManager:
    crystal_type: str = 'Unary'
    unary_crysal: str = ''
    binary_crysal: str = ''
    tertiary_crystal: str = ''

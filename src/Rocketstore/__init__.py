"""
█▀ █▄█ █▀▀ █░█ █▀▀ █░█
▄█ ░█░ █▄▄ █▀█ ██▄ ▀▄▀

Author: <Anton Sychev> (anton at sychev dot xyz) 
__init__.py (c) 2024 
Created:  2024-01-02 17:37:05 
Desc: Inilization of RocketStore
Docs: documentation
"""

__all__ = ["Rocketstore"]

from .__version__ import (
    __author__,
    __author_email__,
    __build__,
    __copyright__,
    __description__,
    __title__,
    __url__,
    __version__,
)

from .Rocketstore import Rocketstore, _ORDER, _ORDER_DESC, _ORDERBY_TIME, _LOCK, _DELETE, _KEYS, _COUNT, _ADD_AUTO_INC, _ADD_GUID, _FORMAT_JSON, _FORMAT_NATIVE, _FORMAT_XML, _FORMAT_PHP

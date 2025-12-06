"""
Módulo Legacy - Wrappers de retrocompatibilidad.

Este módulo contiene wrappers que mantienen la compatibilidad con
la estructura antigua del código. Estos módulos emitirán warnings
de deprecación pero seguirán funcionando.

DEPRECADO: Este módulo será eliminado en la versión 3.0.0
"""

import warnings

warnings.warn(
    "El módulo 'legacy' está deprecado y será eliminado en la versión 3.0.0. "
    "Por favor, actualiza tus imports para usar los nuevos módulos.",
    DeprecationWarning,
    stacklevel=2,
)

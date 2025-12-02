"""Command handlers package - import all handlers to trigger registration"""
from commands.start import handle_start
from commands.help import handle_help

__all__ = ['handle_start', 'handle_help']

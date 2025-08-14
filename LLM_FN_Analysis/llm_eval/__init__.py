"""
LLM Evaluation Package

This package provides functionality for evaluating LLM performance on various tasks.
"""

from .evaluateold import evaluate_with_llm, batch_evaluate

__all__ = ['evaluate_with_llm', 'batch_evaluate']

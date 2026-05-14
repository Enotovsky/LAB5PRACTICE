"""Пользовательские исключения приложения."""

from __future__ import annotations


class BaseAppError(Exception):
    """Базовое исключение приложения."""


class DataFormatError(BaseAppError):
    """Ошибка структуры входного файла."""


class ValidationError(BaseAppError):
    """Ошибка бизнес-валидации записи."""


class InvalidTransactionError(ValidationError):
    """Ошибка структуры или значения отдельной транзакции."""


class CurrencyMismatchError(ValidationError):
    """Ошибка смешанных валют в одном отчете."""

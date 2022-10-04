# -*- coding: utf-8 -*-

import inspect
from six import with_metaclass
import logging
from functools import wraps
import traceback

log = logging.getLogger(__name__)


def _run_on_failure_decorator(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        except Exception as err:
            self = args[0]
            if hasattr(self, "get_traceback") and self._traceback_enabled:
                log.error(
                    f"The method '{wrapper.__name__}' with args: '{args}' and kwargs: {kwargs} \
                    have failed with the following traceback:\n \
                    {self.get_traceback()}"
                )
            if hasattr(self, '_run_on_failure'):
                self._run_on_failure()
            raise err

    return wrapper


class KeywordGroupMetaClass(type):
    def __new__(cls, clsname, bases, dict):
        for name, method in dict.items():
            if not name.startswith('_') and inspect.isroutine(method):
                dict[name] = _run_on_failure_decorator(method)
        return type.__new__(cls, clsname, bases, dict)


class KeywordGroup(with_metaclass(KeywordGroupMetaClass, object)):
    _traceback_enabled = False

    def set_traceback(self, state: bool):
        """Set Traceback state

        :param state: enable/disable traceback logging

        :return: the previous state
        """
        log.debug(f"Set traceback log to: {state}")
        old_value = self._traceback_enabled
        self._traceback_enabled = state
        return old_value

    def get_traceback(self):
        """Retrieve the last exception stack (traceback).
        Usefull feature for to get the exception route cause.

        :return: the exception traceback.
        """
        return traceback.format_exc()

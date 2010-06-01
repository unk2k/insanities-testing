# -*- coding: utf-8 -*-
import gettext


def N_(msg):
    '''gettext marker'''
    return msg

class M_(unicode):
    def __new__(cls, single, plural):
        self = unicode.__new__(cls, single)
        self.plural = plural
        return self


def smart_gettext(translation, msg, count=None):
    if count is None:
        count = 1
    if isinstance(msg, M_) and count is not None:
        return translation.ungettext(msg, msg.plural, count)
    return translation.ugettext(msg)


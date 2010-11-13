# -*- coding: utf-8 -*-

import unittest

from insanities.forms import *
from webob.multidict import MultiDict


class FormClassInitializationTests(unittest.TestCase):

    def test_init(self):
        'Initialization of form object'
        class _Form(Form):
            fields=[
                Field('first', convs.Int()),
                Field('second', convs.Int()),
            ]
        form = _Form()
        self.assertEqual(form.initial, {})
        self.assertEqual(form.raw_data, {'first':'', 'second':''})
        self.assertEqual(form.python_data, {'first':None, 'second':None})

    def test_with_default(self):
        'Initialization of form object with fields default values'
        class _Form(Form):
            fields=[
                Field('first', convs.Int(), default=1),
                Field('second', convs.Int(), get_default=lambda: 2),
            ]
        form = _Form()
        self.assertEqual(form.initial, {})
        self.assertEqual(form.raw_data, {'first':'1', 'second':'2'})
        self.assertEqual(form.python_data, {'first':1, 'second':2})

    def test_with_initial(self):
        'Initialization of form object with initial values'
        class _Form(Form):
            fields=[
                Field('first', convs.Int()),
                Field('second', convs.Int()),
            ]
        form = _Form(initial={'first':1, 'second':2})
        self.assertEqual(form.initial, {'first':1, 'second':2})
        self.assertEqual(form.raw_data, {'first':'1', 'second':'2'})
        self.assertEqual(form.python_data, {'first':1, 'second':2})

    def test_with_initial_and_default(self):
        'Initialization of form object with initial and default values'
        class _Form(Form):
            fields=[
                Field('first', convs.Int(), default=3),
                Field('second', convs.Int()),
            ]
        form = _Form(initial={'first':1, 'second':2})
        self.assertEqual(form.initial, {'first':1, 'second':2})
        self.assertEqual(form.raw_data, {'first':'1', 'second':'2'})
        self.assertEqual(form.python_data, {'first':1, 'second':2})


class FormClassAcceptTests(unittest.TestCase):
    def test_accept(self):
        'Clean accept'
        class _Form(Form):
            fields=[
                Field('first', convs.Int()),
                Field('second', convs.Int()),
            ]
        form = _Form()
        self.assert_(form.accept(MultiDict(first='1', second='2')))
        self.assertEqual(form.initial, {})
        self.assertEqual(form.raw_data, {'first':'1', 'second':'2'})
        self.assertEqual(form.python_data, {'first':1, 'second':2})

    def test_with_default(self):
        'Accept with default values'
        class _Form(Form):
            fields=[
                Field('first', convs.Int(), default=2),
                Field('second', convs.Int(required=False), get_default=lambda: 2),
            ]
        form = _Form()
        self.assert_(form.accept(MultiDict(first='1')))
        self.assertEqual(form.initial, {})
        self.assertEqual(form.python_data, {'first':1, 'second':None})

    def test_with_initial(self):
        'Accept with initial data'
        class _Form(Form):
            fields=[
                Field('first', convs.Int()),
                Field('second', convs.Int()),
            ]
        form = _Form(initial={'second':3})
        self.assert_(form.accept(MultiDict(first='1', second='2')))
        self.assertEqual(form.initial, {'second':3})
        self.assertEqual(form.python_data, {'first':1, 'second':2})

    def test_with_errors(self):
        'Accept with errors'
        class _Form(Form):
            fields=[
                Field('first', convs.Int()),
                Field('second', convs.Int()),
            ]
        form = _Form()
        self.assert_(not form.accept(MultiDict(first='1')))
        self.assertEqual(form.errors, {'second':'required field'})


class FormReadonlyFieldsTest(unittest.TestCase):

    def test_readonly(self):
        'Accept of readonly fields'
        class _Form(Form):
            fields=[
                Field('first', convs.Int(), permissions='r'),
                Field('second', convs.Int()),
            ]
        form = _Form()
        self.assert_(form.accept(MultiDict(first='1', second='2')))
        self.assertEqual(form.python_data, {'first':None, 'second':2})

    def test_with_default(self):
        'Accept of readonly fields with default values'
        class _Form(Form):
            fields=[
                Field('first', convs.Int(), default=1, permissions='r'),
                Field('second', convs.Int()),
            ]
        form = _Form()
        self.assert_(form.accept(MultiDict(first='3', second='2')))
        self.assertEqual(form.python_data, {'first':1, 'second':2})
        self.assertEqual(form.raw_data, {'first':'1', 'second':'2'})

    def test_fieldset(self):
        'Accept of readonly fieldset with default values'
        class _Form(Form):
            fields=[
                FieldSet('set', fields=[
                    Field('first', convs.Int(), default=1, permissions='r'),
                    Field('second', convs.Int(), default=2),
                ]),
                Field('third', convs.Int()),
            ]
        form = _Form()
        self.assert_(form.accept(MultiDict(**{'set.first': '2', 'set.second': '2', 'third': '3'})))
        self.assertEqual(form.python_data, {'set': {'first': 1, 'second': 2}, 'third': 3})
        self.assertEqual(form.raw_data, MultiDict(**{'set.first': '1', 'set.second': '2', 'third':'3'}))

    def test_fieldlist(self):
        'Accept of readonly fieldlist with default values'
        class _Form(Form):
            fields=[
                FieldList('list', field=Field('number', convs.Int(), permissions='r')),
            ]
        form = _Form(initial={'list':[1, 2]})
        self.assertEqual(form.raw_data, MultiDict((('list-indeces', '1'), ('list-indeces', '2')), **{'list-1': '1', 'list-2': '2'}))
        self.assertEqual(form.python_data, {'list': [1, 2]})
        self.assert_(form.accept(MultiDict((('list-indeces', '1'), ('list-indeces', '2')), **{'list-1': '2', 'list-2': '3'})))
        self.assertEqual(form.python_data, {'list': [1, 2]})

    def test_fieldlist_of_fieldsets(self):
        'Accept of fieldlist of readonly fieldsets'
        class _Form(Form):
            fields=[
                FieldList('list', field=FieldSet(
                    'set',
                    fields=[Field('number', convs.Int(), permissions='r')],
                )),
            ]
        form = _Form(initial={'list':[{'number':1}, {'number':2}]})
        self.assertEqual(form.raw_data, MultiDict((('list-indeces', '1'), ('list-indeces', '2')), **{'list-1.number': '1', 'list-2.number': '2'}))
        self.assertEqual(form.python_data, {'list': [{'number':1}, {'number':2}]})
        self.assert_(form.accept(MultiDict((('list-indeces', '1'), ('list-indeces', '2')), **{'list-1.number': '2', 'list-2.number': '3'})))
        self.assertEqual(form.python_data, {'list': [{'number':1}, {'number':2}]})

    def test_fieldset_of_fieldsets(self):
        'Accept of readonly fieldset of fieldsets'
        class _Form(Form):
            fields=[
                FieldSet('sets', fields=[
                    FieldSet('set1', fields=[
                        Field('first', convs.Int(), permissions='r'),
                        Field('second', convs.Int()),
                    ]),
                    FieldSet('set2', fields=[
                        Field('first', convs.Int()),
                        Field('second', convs.Int(), permissions='r'),
                    ]),
                ]),
            ]
        form = _Form(initial={'sets':{
            'set1': {'first': 1, 'second': 2},
            'set2': {'first': 1, 'second': 2},
        }})

        self.assertEqual(form.raw_data, MultiDict(**{
            'sets.set1.first': '1',
            'sets.set1.second': '2',
            'sets.set2.first': '1',
            'sets.set2.second': '2',
        }))

        self.assert_(form.accept(MultiDict(**{
            'sets.set1.first': 'incorect',
            'sets.set1.second': '2',
            'sets.set2.first': '1',
            'sets.set2.second': 'incorect',
        })))

        self.assertEqual(form.python_data, {'sets': {
            'set1': {'first': 1, 'second': 2}, 
            'set2': {'first': 1, 'second': 2}, 
        }})

        self.assertEqual(form.raw_data, MultiDict(**{
            'sets.set1.first': '1',
            'sets.set1.second': '2',
            'sets.set2.first': '1',
            'sets.set2.second': '2',
        }))

    def test_fieldset_of_fieldsets_with_noreq(self):
        'Accept of readonly fieldset of fieldsets with required=False'
        class _Form(Form):
            fields=[
                FieldSet('sets', fields=[
                    FieldSet('set1', fields=[
                        Field('first', convs.Int(required=False), permissions='r'),
                        Field('second', convs.Int()),
                    ]),
                    FieldSet('set2', fields=[
                        Field('first', convs.Int()),
                        Field('second', convs.Int(required=False), permissions='r'),
                    ]),
                ]),
            ]
        form = _Form(initial={'sets':{
            'set1': {'first': None, 'second': 2},
            'set2': {'first': 1, 'second': None},
        }})

        self.assertEqual(form.raw_data, MultiDict(**{
            'sets.set1.first': '',
            'sets.set1.second': '2',
            'sets.set2.first': '1',
            'sets.set2.second': '',
        }))

        self.assert_(form.accept(MultiDict(**{
            'sets.set1.first': 'incorect',
            'sets.set1.second': '2',
            'sets.set2.first': '1',
            'sets.set2.second': 'incorect',
        })))

        self.assertEqual(form.python_data, {'sets': {
            'set1': {'first': None, 'second': 2}, 
            'set2': {'first': 1, 'second': None}, 
        }})

        self.assertEqual(form.raw_data, MultiDict(**{
            'sets.set1.first': '',
            'sets.set1.second': '2',
            'sets.set2.first': '1',
            'sets.set2.second': '',
        }))

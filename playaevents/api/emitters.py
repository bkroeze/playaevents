#!/usr/bin/env python
# encoding: utf-8
"""
emitters.py

Created by Ariel Nunez on 2009-05-24.  Ported to PlayaEvents by Bruce Kroeze 2011-06-10
Copyright (c) 2011 Black Rock City LLC. All rights reserved.
"""
from __future__ import generators

import types, decimal, re, inspect

from piston.emitters import JSONEmitter
from piston.utils import HttpStatusCode
from django.db.models.query import QuerySet
from django.db.models import Model, permalink

from django.utils.encoding import smart_unicode
from django.http import HttpResponse

try:
    import simplejson
except ImportError:
    from django.utils import simplejson


class TimeAwareJSONEmitter(JSONEmitter):
    """
    JSON emitter, understands timestamps.
    """

    def construct(self):
        """
        Recursively serialize a lot of types, and
        in cases where it doesn't recognize the type,
        it will fall back to Django's `smart_unicode`.

        Returns `dict`.
        """
        def _any(thing, fields=()):
            """
            Dispatch, all types are routed through here.
            """
            ret = None

            if isinstance(thing, QuerySet):
                ret = _qs(thing, fields=fields)
            elif isinstance(thing, (tuple, list)):
                ret = _list(thing)
            elif isinstance(thing, dict):
                ret = _dict(thing)
            elif isinstance(thing, decimal.Decimal):
                ret = str(thing)
            elif isinstance(thing, Model):
                ret = _model(thing, fields=fields)
            elif isinstance(thing, HttpResponse):
                raise HttpStatusCode(thing)
            elif isinstance(thing, types.FunctionType):
                if not inspect.getargspec(thing)[0]:
                    ret = _any(thing())
            else:
                ret = smart_unicode(thing, strings_only=True)

            return ret

        def _fk(data, field):
            """
            Foreign keys.
            """
            return _any(getattr(data, field.name))

        def _related(data, fields=()):
            """
            Foreign keys.
            """
            return [ _model(m, fields) for m in data.iterator() ]

        def _m2m(data, field, fields=()):
            """
            Many to many (re-route to `_model`.)
            """
            return [ _model(m, fields) for m in getattr(data, field.name).iterator() ]

        def _model(data, fields=()):
            """
            Models. Will respect the `fields` and/or
            `exclude` on the handler (see `typemapper`.)
            """
            ret = { }
            handler = self.in_typemapper(type(data), self.anonymous)
            get_absolute_uri = False

            if handler or fields:
                v = lambda f: getattr(data, f.attname)

                if not fields:
                    """
                    Fields was not specified, try to find the correct
                    version in the typemapper we were sent.
                    """
                    mapped = self.in_typemapper(type(data), self.anonymous)
                    get_fields = set(mapped.fields)
                    exclude_fields = set(mapped.exclude).difference(get_fields)

                    if 'absolute_uri' in get_fields:
                        get_absolute_uri = True

                    if not get_fields:
                        get_fields = set([ f.attname.replace("_id", "", 1)
                            for f in data._meta.fields ])

                    # sets can be negated.
                    for exclude in exclude_fields:
                        if isinstance(exclude, basestring):
                            get_fields.discard(exclude)

                        elif isinstance(exclude, re._pattern_type):
                            for field in get_fields.copy():
                                if exclude.match(field):
                                    get_fields.discard(field)

                else:
                    get_fields = set(fields)

                met_fields = self.method_fields(handler, get_fields)

                for f in data._meta.local_fields:
                    if f.serialize and f.attname not in met_fields:
                        if not f.rel:
                            if f.attname in get_fields:
                                ret[f.attname] = _any(v(f))
                                get_fields.remove(f.attname)
                        else:
                            if f.attname[:-3] in get_fields:
                                ret[f.name] = _fk(data, f)
                                get_fields.remove(f.name)

                for mf in data._meta.many_to_many:
                    if mf.serialize and mf.attname not in met_fields:
                        if mf.attname in get_fields:
                            ret[mf.name] = _m2m(data, mf)
                            get_fields.remove(mf.name)

                # try to get the remainder of fields
                for maybe_field in get_fields:

                    if isinstance(maybe_field, (list, tuple)):
                        model, fields = maybe_field
                        inst = getattr(data, model, None)

                        if inst:
                            if hasattr(inst, 'all'):
                                ret[model] = _related(inst, fields)
                            elif callable(inst):
                                if len(inspect.getargspec(inst)[0]) == 1:
                                    ret[model] = _any(inst(), fields)
                            else:
                                ret[model] = _model(inst, fields)

                    elif maybe_field in met_fields:
                        # Overriding normal field which has a "resource method"
                        # so you can alter the contents of certain fields without
                        # using different names.
                        ret[maybe_field] = _any(met_fields[maybe_field](data))

                    else:
                        maybe = getattr(data, maybe_field, None)
                        if maybe:
                            if isinstance(maybe, (int, basestring)):
                                ret[maybe_field] = _any(maybe)
                            elif callable(maybe):
                                if len(inspect.getargspec(maybe)[0]) == 1:
                                    ret[maybe_field] = _any(maybe())
                        else:
                            handler_f = getattr(handler or self.handler, maybe_field, None)

                            if handler_f:
                                ret[maybe_field] = _any(handler_f(data))

            else:
                for f in data._meta.fields:
                    ret[f.attname] = _any(getattr(data, f.attname))

                fields = dir(data.__class__) + ret.keys()
                add_ons = [k for k in dir(data) if k not in fields]

                for k in add_ons:
                    ret[k] = _any(getattr(data, k))

            # resource uri
            if self.in_typemapper(type(data), self.anonymous):
                handler = self.in_typemapper(type(data), self.anonymous)
                if hasattr(handler, 'resource_uri'):
                    url_id, fields = handler.resource_uri()
                    ret['resource_uri'] = permalink( lambda: (url_id,
                        (getattr(data, f) for f in fields) ) )()

            if hasattr(data, 'get_api_url') and 'resource_uri' not in ret:
                try: ret['resource_uri'] = data.get_api_url()
                except: pass

            # absolute uri
            if hasattr(data, 'get_absolute_url') and get_absolute_uri:
                try: ret['absolute_uri'] = data.get_absolute_url()
                except: pass

            return ret

        def _qs(data, fields=()):
            """
            Querysets.
            """
            return [ _any(v, fields) for v in data ]

        def _list(data):
            """
            Lists.
            """
            return [ _any(v) for v in data ]

        def _dict(data):
            """
            Dictionaries.
            """
            return dict([ (k, _any(v)) for k, v in data.iteritems() ])

        # Kickstart the seralizin'.
        return _any(self.data, self.fields)

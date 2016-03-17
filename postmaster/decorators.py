"""
Author: StackFocus
File: decorators.py
Purpose: defines decorators for the app
"""

import functools
from flask import jsonify, request, url_for


def json_wrap(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        rv = f(*args, **kwargs)
        status_or_headers = None
        headers = None
        if isinstance(rv, tuple):
            rv, status_or_headers, headers = rv + (None, ) * (3 - len(rv))
        if isinstance(status_or_headers, (dict, list)):
            headers, status_or_headers = status_or_headers, None
        if not isinstance(rv, dict):
            rv = rv.to_json()
        rv = jsonify(rv)
        if status_or_headers is not None:
            rv.status_code = status_or_headers
        if headers is not None:
            rv.headers.extend(headers)
        return rv

    return wrapped


def paginate(max_per_page=10):
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page',
                                            max_per_page,
                                            type=int),
                           max_per_page)
            query = f(*args, **kwargs)
            p = query.paginate(page, per_page)
            pages = {
                'page': page,
                'per_page': per_page,
                'total': p.total,
                'pages': p.pages
            }
            if p.has_prev:
                pages['prev'] = url_for(request.endpoint, page=p.prev_num,
                                        per_page=per_page,
                                        _external=True, **kwargs)
            else:
                pages['prev'] = None
            if p.has_next:
                pages['next'] = url_for(request.endpoint, page=p.next_num,
                                        per_page=per_page,
                                        _external=True, **kwargs)
            else:
                pages['next'] = None
            pages['first'] = url_for(request.endpoint, page=1,
                                     per_page=per_page, _external=True,
                                     **kwargs)
            pages['last'] = url_for(request.endpoint, page=p.pages,
                                    per_page=per_page, _external=True,
                                    **kwargs)
            return jsonify({
                'items': [item.to_json() for item in p.items],
                'meta': pages
            })

        return wrapped

    return decorator

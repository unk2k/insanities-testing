# -*- coding: utf-8 -*-

import datetime, os

from forms import FileForm
from webob.exc import HTTPSeeOther

from insanities.ext.filefields import time_uid


def render_to(template):
    def wrap(env, data, next_handler):
        template_args = dict(data.as_dict(), url_for=env.url_for)
        return env.template.render_to_response(template, template_args)
    return wrap


def list_files(env, data, next_handler):
    dir_ = os.path.join(env.cfg.MEDIA, 'stored')
    if not os.path.isdir(dir_):
        os.makedirs(dir_)
    data.files = os.listdir(dir_)
    data.form = FileForm(env)
    data.url = '/media/stored/'
    return next_handler(env, data)

def post_file(env, data, next_handler):
    dir_ = os.path.join(env.cfg.MEDIA, 'stored')
    form = data.form

    if form.accept(env.request.POST, env.request.FILES):
        tmp_file = form.python_data['file']
        if tmp_file.mode == 'temp':
            filename = time_uid() + tmp_file.ext
            new_path = os.path.join(dir_, filename)
            os.rename(tmp_file.full_path, new_path)

        raise HTTPSeeOther(location=str(env.url_for('files')))
    #result = dict(result)
    return next_handler(env, data)


def delete_files(env, data, next_handler):
    dir_ = os.path.join(env.cfg.MEDIA, 'stored')
    f = env.request.GET.get('filename', '')
    filepath = os.path.join(dir_, f)
    if '/' not in f and os.path.isfile(filepath):
        os.unlink(filepath)
    raise HTTPSeeOther(location=str(env.url_for('files')))

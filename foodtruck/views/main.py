import os
import os.path
import logging
import bcrypt
from flask import g, request, render_template, url_for, redirect
from flask.ext.login import login_user, logout_user, login_required
from piecrust.configuration import parse_config_header
from piecrust.rendering import QualifiedPage
from piecrust.uriutil import split_uri
from ..views import with_menu_context
from ..web import app, load_user


logger = logging.getLogger(__name__)


@app.route('/')
@login_required
def index():
    from flask.ext.login import current_user
    if not current_user.is_authenticated:
        raise Exception()

    data = {}
    site = g.sites.get()
    assert site is not None

    fs_endpoints = {}
    data['sources'] = []
    for source in site.piecrust_app.sources:
        if source.is_theme_source:
            continue
        facs = source.getPageFactories()
        src_data = {
                'name': source.name,
                'list_url': url_for('list_source', source_name=source.name),
                'page_count': len(facs)}
        data['sources'].append(src_data)

        fe = getattr(source, 'fs_endpoint', None)
        if fe:
            fs_endpoints[fe] = source

    st = site.scm.getStatus()
    data['new_pages'] = []
    for p in st.new_files:
        pd = _getWipData(p, site, fs_endpoints)
        if pd:
            data['new_pages'].append(pd)
    data['edited_pages'] = []
    for p in st.edited_files:
        pd = _getWipData(p, site, fs_endpoints)
        if pd:
            data['edited_pages'].append(pd)

    data['site_name'] = site.name
    data['url_bake'] = url_for('bake_site')
    data['url_preview'] = url_for('preview_site_root', sitename=site.name)

    with_menu_context(data)
    return render_template('dashboard.html', **data)


def _getWipData(path, site, fs_endpoints):
    source = None
    for endpoint, s in fs_endpoints.items():
        if path.startswith(endpoint):
            source = s
            break
    if source is None:
        return None

    fac = source.buildPageFactory(os.path.join(site.root_dir, path))
    route = site.piecrust_app.getRoute(
            source.name, fac.metadata, skip_taxonomies=True)
    if not route:
        return None

    qp = QualifiedPage(fac.buildPage(), route, fac.metadata)
    uri = qp.getUri()
    _, slug = split_uri(site.piecrust_app, uri)

    with open(fac.path, 'r', encoding='utf8') as fp:
        raw_text = fp.read()

    preferred_length = 100
    max_length = 150
    header, offset = parse_config_header(raw_text)
    extract = raw_text[offset:offset + preferred_length]
    if len(raw_text) > offset + preferred_length:
        for i in range(offset + preferred_length,
                       min(offset + max_length, len(raw_text))):
            c = raw_text[i]
            if c not in [' ', '\t', '\r', '\n']:
                extract += c
            else:
                extract += '...'
                break

    return {
            'title': qp.config.get('title'),
            'slug': slug,
            'url': url_for('edit_page', slug=slug),
            'text': extract
            }


@app.route('/bake', methods=['POST'])
def bake_site():
    site = g.sites.get()
    site.bake()
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    data = {}

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember')

        user = load_user(username)
        if user is not None and app.bcrypt:
            if app.bcrypt.check_password_hash(user.password, password):
                login_user(user, remember=bool(remember))
                return redirect(url_for('index'))
        data['message'] = (
                "User '%s' doesn't exist or password is incorrect." %
                username)

    return render_template('login.html', **data)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


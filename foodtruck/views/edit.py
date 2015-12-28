import os.path
import logging
from flask import (
        g, request, abort, render_template, url_for, flash)
from flask.ext.login import login_required
from piecrust.rendering import (
        PageRenderingContext, render_page)
from piecrust.serving.util import get_requested_page
from ..views import with_menu_context
from ..web import app


logger = logging.getLogger(__name__)


@app.route('/edit/', defaults={'slug': ''}, methods=['GET', 'POST'])
@app.route('/edit/<path:slug>', methods=['GET', 'POST'])
@login_required
def edit_page(slug):
    site = g.sites.get().piecrust_app
    rp = get_requested_page(site, '/site/%s/%s' % (g.sites.default_site_name,
                                                   slug))
    page = rp.qualified_page
    if page is None:
        abort(404)

    if request.method == 'POST':
        page_text = request.form['page_text']
        if request.form['is_dos_nl'] == '0':
            page_text = page_text.replace('\r\n', '\n')

        if 'do_preview' in request.form or 'do_save' in request.form:
            logger.debug("Writing page: %s" % page.path)
            with open(page.path, 'w', encoding='utf8') as fp:
                fp.write(page_text)
            flash("%s was saved." % os.path.relpath(page.path, site.root_dir))

        if 'do_preview' in request.form:
            return _preview_page(page)

        if 'do_save' in request.form:
            return _edit_page_form(page)

        abort(400)

    return _edit_page_form(page)


def _preview_page(page):
    render_ctx = PageRenderingContext(page, force_render=True)
    rp = render_page(render_ctx)
    return rp.content


def _edit_page_form(page):
    data = {}
    data['is_new_page'] = False
    data['url_cancel'] = url_for('list_source', source_name=page.source.name)
    with open(page.path, 'r', encoding='utf8') as fp:
        data['page_text'] = fp.read()
    data['is_dos_nl'] = "1" if '\r\n' in data['page_text'] else "0"

    with_menu_context(data)
    return render_template('edit_page.html', **data)


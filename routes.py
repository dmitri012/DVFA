from flask import Flask, render_template, url_for, redirect, request, session
import requests
import forms

from app import app
import db


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

# Fixed Access Control - using server-side sessions
@app.route('/admin')
def admin():    
    # Check server-side session instead of client-controlled cookie
    if session.get('is_admin') == True:
        return render_template('admin.html')
    else:
        return render_template('403.html')

# Admin login endpoint for proper authentication
@app.route('/admin/login', methods=['POST'])
def admin_login():
    # This should verify credentials against a secure backend
    # For example: check username/password against database with hashed passwords
    username = request.form.get('username')
    password = request.form.get('password')
    
    # TODO: Implement proper authentication logic here
    # Example: verify_credentials(username, password)
    # For now, this prevents unauthorized access via cookie manipulation
    # In production, implement proper authentication with hashed passwords
    
    # Only set session after successful authentication
    # session['is_admin'] = True
    
    return redirect(url_for('admin'))

# Admin logout endpoint
@app.route('/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

# SSRF
@app.route('/analyzer')
def follow_url():
    url = request.args.get('url', '')
    if url:
        r = requests.get(url)
        return render_template('analyzer.html', req=r)
    else:
        return render_template('analyzer-empty-state.html')
    """
    Prevention:
        import ipaddress
        import socket
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        ip = socket.gethostbyname(domain)
        if(not ipaddress.ip_address(ip).is_private):
            return render_template('analyzer.html', req=r)
        else:
            return render_template('analyzer-empty-state.html')
    """

# XSS, CSRF (no CSRF-Token)
@app.route('/guestbook', methods=['GET', 'POST'])
def guestbook():
    search_query = request.args.get('q')
    comments = db.get(search_query)

    form = forms.AddCommentForm()
    if form.validate_on_submit():
        db.add(form.comment.data)

        return redirect(url_for('guestbook'))
    return render_template('guestbook.html', form=form, comments=comments, search_query=search_query)
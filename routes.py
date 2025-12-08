from flask import Flask, render_template, url_for, redirect, request, session
import requests
import forms

from app import app
import db


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

# Server-side session-based access control
@app.route('/admin')
def admin():    
    # Check server-side session instead of client-controlled cookie
    if session.get('is_admin') is True:
        return render_template('admin.html')
    else:
        return render_template('403.html')

# Login route to authenticate users and set session variables
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Authenticate user against database
        user = db.authenticate_user(username, password)
        if user:
            # Set server-side session variables (not client-controlled)
            session['logged_in'] = True
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            return redirect(url_for('admin') if user['is_admin'] else url_for('index'))
        else:
            return render_template('login.html', form=form, error='Invalid credentials')
    
    return render_template('login.html', form=form, error=None)

# Logout route to clear session
@app.route('/logout')
def logout():
    session.clear()
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
from flask import Flask, render_template, url_for, redirect, request, session
import requests
import forms
import ipaddress
import socket
from urllib.parse import urlparse

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

# URL analyzer with SSRF protection
@app.route('/analyzer')
def follow_url():
    url = request.args.get('url', '')
    if url:
        # Validate URL to prevent SSRF attacks
        if not is_safe_url(url):
            return render_template('analyzer-empty-state.html', error='Invalid or unsafe URL')
        
        try:
            r = requests.get(url, timeout=5)
            return render_template('analyzer.html', req=r)
        except requests.exceptions.RequestException:
            return render_template('analyzer-empty-state.html', error='Failed to fetch URL')
    else:
        return render_template('analyzer-empty-state.html')


def is_safe_url(url):
    """
    Validate URL to prevent SSRF attacks.
    Checks:
    - Scheme is http or https only
    - Hostname is in allowlist
    - IP address is not private, loopback, link-local, or multicast
    """
    try:
        parsed = urlparse(url)
        
        # Validate scheme - only allow http and https
        if parsed.scheme not in ('http', 'https'):
            return False
        
        # Extract hostname
        hostname = parsed.hostname
        if not hostname:
            return False
        
        # Allowlist of permitted domains
        # Modify this list based on your application's requirements
        allowed_domains = [
            'example.com',
            'www.example.com',
            'api.example.com',
            # Add other trusted domains here
        ]
        
        # Check if hostname is in allowlist
        if hostname not in allowed_domains:
            return False
        
        # Resolve hostname to IP address and validate
        try:
            ip = socket.gethostbyname(hostname)
            ip_obj = ipaddress.ip_address(ip)
            
            # Block private, loopback, link-local, and multicast addresses
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast:
                return False
        except (socket.gaierror, ValueError):
            # DNS resolution failed or invalid IP
            return False
        
        return True
    except Exception:
        return False

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
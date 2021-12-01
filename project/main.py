# main.py

from flask import Blueprint, render_template, redirect, url_for, request, session

import datetime
from flask_login import login_required, current_user
from project import app
from .models import User, Token
from . import db
from project.helpers import pelm_helpers

main = Blueprint('main', __name__)

EMAIL = 'stout@gmail.com'
PASSWORD = 'password'

BASE_64_ENCODED_STRING = 'NTAwOGQwNmEtNGU0NC0xMWVjLWFjZTMtYWNkZTQ4MDAxMTIyOmM1NjFjZjQ4MWY2YzU5MjRlMzA2NjU3NjkyODQ4ODEyNWEyMTgwZDhhNmNlMDhhMTI1ZTRkZTA4ZWViZDRkMzU='

@main.route('/')
@login_required
def index():
    token = current_user.token

    if not token or not token.refresh_token_expiration or datetime.datetime.now() > token.refresh_token_expiration:
        return redirect(url_for('main.authorize_user'))

    pelm_user_id = current_user.pelm_user_id
    energy_account_ids = pelm_helpers.get_energy_accounts(pelm_user_id)
    data = session.get('interval_data')
    if data:
        session.pop('interval_data')

    return render_template('index.html', pelm_user_id=pelm_user_id, unique_account_ids=energy_account_ids, interval_data=data)


@app.route('/data', methods=['GET'])
def get_data():
    account_id = request.args.get('unique_account_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    interval_data = pelm_helpers.get_energy_data_for_account(account_id, start_date, end_date)
    session['interval_data'] = interval_data

    return redirect(url_for('main.index'))


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


@main.route('/user/authorize')
def authorize_user():
    redirect_url = '{STOUT_URL}/redirect'.format(STOUT_URL=app.config.get('STOUT_URL'))
    return render_template('connect_utility.html', redirect_url=redirect_url)


@main.route('/pelm/authorize')
def authorize_user_post():
    url = "{url}?client_id={client_id}".format(
        url="{host}/users/authorize".format(host=app.config.get('PELM_API_URL')),
        client_id=app.config.get('PELM_CLIENT_ID')
    )

    return redirect(url)


@main.route('/redirect', methods=['GET'])
def pelm_redirect():
    unique_id = request.args.get('unique_id')
    code = request.args.get('code')

    tokens = pelm_helpers.exchange_authorization_code_for_access_token(code)

    current_user.set_pelm_user_id(unique_id)
    new_token = Token(user_id=current_user.id,
                      access_token=tokens['access_token'],
                      refresh_token=tokens['refresh_token'],
                      access_token_expiration=datetime.datetime.now() + datetime.timedelta(seconds=tokens['access_token_expires_in']),
                      refresh_token_expiration=datetime.datetime.now() + datetime.timedelta(seconds=tokens['refresh_token_expires_in']),
                      )
    db.session.add(new_token)
    db.session.commit()

    return redirect(url_for('main.index'))
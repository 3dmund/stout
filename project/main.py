# main.py

from flask import Blueprint, render_template, redirect, url_for, request, session
# from flask import Flask, abort, request, jsonify, g, url_for, redirect, render_template, flash

import datetime
from flask_login import login_required, current_user
from project import app
from requests import post, get
from requests.auth import HTTPBasicAuth
from .models import User, Token
from . import db

import base64

main = Blueprint('main', __name__)

EMAIL = 'stout@gmail.com'
PASSWORD = 'password'

BASE_64_ENCODED_STRING = 'NTAwOGQwNmEtNGU0NC0xMWVjLWFjZTMtYWNkZTQ4MDAxMTIyOmM1NjFjZjQ4MWY2YzU5MjRlMzA2NjU3NjkyODQ4ODEyNWEyMTgwZDhhNmNlMDhhMTI1ZTRkZTA4ZWViZDRkMzU='

@main.route('/')
@login_required
def index():
    print("Loading indexs")

    pelm_user_id = current_user.pelm_user_id
    token = current_user.token

    # TODO: check if token is expired

    if not token or not token.refresh_token_expiration or datetime.datetime.now() > token.refresh_token_expiration:
        return redirect(url_for('main.authorize_user'))

    # if not pelm_user_id:
    #     return redirect(url_for('main.connect_utility'))

    data = session.get('interval_data')
    if data:
        session.pop('interval_data')

    energy_account_ids = get_energy_accounts(pelm_user_id)

    return render_template('index.html', pelm_user_id=pelm_user_id, unique_account_ids=energy_account_ids, interval_data=data)


@app.route('/data', methods=['GET'])
def get_data():
    print("getting data")

    account_id = request.args.get('unique_account_id')

    print("unique_account_id: {}".format(account_id))

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    access_token = current_user.token.access_token

    url = '{PELM_API_URL}/accounts/{account_id}/intervals?start_date={start_date}&end_date={end_date}'.format(
        PELM_API_URL=app.config.get('PELM_API_URL'),
        account_id=account_id,
        start_date=start_date,
        end_date=end_date
    )

    headers = {
        'Authorization': 'Bearer {}'.format(access_token)
    }

    response = get(url=url, headers=headers)

    session['interval_data'] = response.text

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
    print("authorizing user")
    url = "{host}/users/authorize".format(host=app.config.get('PELM_API_URL'))
    print(url)

    url_with_params = "{url}?client_id={client_id}".format(
        url=url,
        client_id=app.config.get('PELM_CLIENT_ID')
    )

    return redirect(url_with_params)

@main.route('/redirect', methods=['GET'])
def pelm_redirect():
    print("hit redirect")
    print(request.args)
    unique_id = request.args.get('unique_id')
    code = request.args.get('code')
    print(f"unique_id: {unique_id}")

    tokens = exchange_authorization_code_for_access_token(code)
    # access_token, refresh_token = exchange_authorization_code_for_access_token(code)
    print(tokens)

    # time_delta = datetime.timedelta(seconds)

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


# def get_pelm_auth_token():
#     print("getting pelm auth token")
#     url = '{PELM_API_URL}/auth/refresh'.format(
#         PELM_API_URL=app.config.get('PELM_API_URL'),
#     )
#
#     data = {
#         'email': EMAIL,
#         'password': PASSWORD
#     }
#
#     response = post(url, data=data)
#     response_json = response.json()
#
#     print(response_json)
#     return response_json.get('auth_token')

def get_access_token():
    current_time = datetime.datetime.now()
    token = current_user.token

    # Throw if refresh expired
    if not token or not token.refresh_token or token.refresh_token_expiration < current_time:
        raise Exception("Must authorize user")

    if current_time < token.access_token_expiration:
        return token.access_token

    print("refreshing access_token")
    pelm_token_url = '{PELM_API_URL}/auth/token'.format(
        PELM_API_URL=app.config.get('PELM_API_URL')
    )

    data = {
        'grant_type': 'refresh_token',
        'redirect_url': '{}/redirect'.format(app.config.get('STOUT_URL'))
    }

    headers = {
        'Authorization': f'Basic {token.refresh_token}'
    }

    response = post(pelm_token_url, data=data, headers=headers)

    print(response)

    print(response.text)

    data = response.json()['data']

    access_token = data['access_token']
    refresh_token = data['refresh_token']



    token.update_token(access_token=data['access_token'],
                       refresh_token=data['refresh_token'],
                       access_token_expiration=data['access_token_expiration'],
                       refresh_token_expiration=data['refresh_token_expiration'])

    db.session.commit()


    print("refresh token worked")
    print(token)


    return token.access_token


def get_energy_accounts(unique_id):
    print("get energy accounts")
    access_token = get_access_token()

    url = '{PELM_API_URL}/users/{unique_id}/accounts'.format(
        PELM_API_URL=app.config.get('PELM_API_URL'),
        unique_id=unique_id,
    )

    headers = {
        'Authorization': 'Bearer {}'.format(access_token)
    }

    response = get(url, headers=headers)

    print("response")
    print(response)
    print(response.json())

    return response.json()['account_ids']

def exchange_authorization_code_for_access_token(code):
    print("getting access_token")
    url = '{PELM_API_URL}/auth/token'.format(
        PELM_API_URL=app.config.get('PELM_API_URL')
    )

    data = {
        'grant_type': 'code',
        'code': code,
        'redirect_url': '{}/redirect'.format(app.config.get('STOUT_URL'))
    }


    auth = HTTPBasicAuth(app.config.get('PELM_CLIENT_ID'), app.config.get('PELM_CLIENT_SECRET'))


    response = post(url, data=data, auth=auth)

    print(response)

    print(response.text)

    data = response.json()

    return data


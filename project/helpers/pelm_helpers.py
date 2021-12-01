from flask import Blueprint, render_template, redirect, url_for, request, session
# from flask import Flask, abort, request, jsonify, g, url_for, redirect, render_template, flash

import datetime
from flask_login import login_required, current_user
from project import app
from requests import post, get
from requests.auth import HTTPBasicAuth
from project.models import User, Token
from project import db


def get_energy_accounts(unique_id):
    access_token = get_access_token()

    url = '{PELM_API_URL}/users/{unique_id}/accounts'.format(
        PELM_API_URL=app.config.get('PELM_API_URL'),
        unique_id=unique_id,
    )
    headers = {
        'Authorization': 'Bearer {}'.format(access_token)
    }
    response = get(url, headers=headers)

    return response.json()['account_ids']


def get_energy_data_for_account(account_id, start_date, end_date):
    access_token = get_access_token()

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

    return response.text


def exchange_authorization_code_for_access_token(code):
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

    return response.json()


def get_access_token():
    current_time = datetime.datetime.now()
    token = current_user.token

    if not token or not token.refresh_token or token.refresh_token_expiration < current_time:
        raise Exception("Must authorize user")

    if token.access_token_expiration < current_time:
        refresh_access_token()

    return current_user.token.access_token


def refresh_access_token():
    token = current_user.token

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
    data = response.json()['data']

    token.update_token(access_token=data['access_token'],
                       access_token_expiration=data['access_token_expiration'])
    db.session.commit()
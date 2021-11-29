# main.py

from flask import Blueprint, render_template, redirect, url_for, request, session
# from flask import Flask, abort, request, jsonify, g, url_for, redirect, render_template, flash

from flask_login import login_required, current_user
from project import app
from requests import post, get

import base64

main = Blueprint('main', __name__)

EMAIL = 'stout@gmail.com'
PASSWORD = 'password'

BASE_64_ENCODED_STRING = 'NTAwOGQwNmEtNGU0NC0xMWVjLWFjZTMtYWNkZTQ4MDAxMTIyOmM1NjFjZjQ4MWY2YzU5MjRlMzA2NjU3NjkyODQ4ODEyNWEyMTgwZDhhNmNlMDhhMTI1ZTRkZTA4ZWViZDRkMzU='

@main.route('/')
@login_required
def index():
    # TODO: check if we have token in db and redirect to connect utility page if we don't

    print("Loading indexs")
    unique_id = request.args.get('unique_id')

    if not unique_id:
        return redirect(url_for('main.connect_utility'))

    data = session.get('interval_data')
    if data:
        session.pop('interval_data')

    access_token = request.args.get('access_token')

    energy_account_ids = get_energy_accounts(unique_id, access_token)

    print(f"energy_account_ids: {energy_account_ids}")

    return render_template('index.html', unique_id=unique_id, unique_account_ids=energy_account_ids, access_token=access_token, interval_data=data)


@app.route('/data', methods=['GET'])
def get_data():
    print("getting data")

    unique_id = request.args.get('unique_id')

    account_id = request.args.get('unique_account_id')

    print("unique_account_id: {}".format(account_id))

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    access_token = request.args.get('access_token')

    url = '{PELM_API_URL}/intervals/get?account_id={account_id}&start_date={start_date}&end_date={end_date}'.format(
        PELM_API_URL=app.config.get('PELM_API_URL'),
        account_id=account_id,
        start_date=start_date,
        end_date=end_date
    )

    headers = {
        'Authorization': 'Bearer {}'.format(access_token)
    }

    print(url)

    response = get(url=url, headers=headers)

    print(response)
    print(response.json())

    # data = {
    #     'data': response.json()
    # }

    session['interval_data'] = response.text

    # return get(url=url_for('main.index'), data=data)

    redirect_url = f'{url_for("main.index")}?unique_id={unique_id}&access_token={access_token}'

    return redirect(redirect_url)

    # return render_template('home.html', unique_id=unique_id, unique_account_ids=unique_account_ids)

    # return response.text




@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

@main.route('/connect/utility')
def connect_utility():
    redirect_url = '{STOUT_URL}/redirect'.format(STOUT_URL=app.config.get('STOUT_URL'))
    return render_template('connect_utility.html', redirect_url=redirect_url)

@main.route('/pelm/authorize')
def connect_utility_post():
    print("authorizing user")
    url = "{host}/auth/authorize".format(host=app.config.get('PELM_API_URL'))
    print(url)

    # headers = {
    # 	'Authorization': 'Basic {}'.format(get_pelm_auth_token())
    # }
    #
    # response = post(url=url, headers=headers)
    # print(response)
    # print(type(response))
    # # print(response.get_data)

    # token = get_pelm_auth_token()
    # print(f"token: {token}")

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

    # TODO: we're passing this along for now. Should save to db.
    access_token = get_access_token(code)
    print(access_token)

    redirect_url = '{url}?unique_id={unique_id}&access_token={access_token}'.format(
        url=url_for('main.index'),
        unique_id=unique_id,
        access_token=access_token
    )

    # return unique_id

    return redirect(redirect_url)



def get_pelm_auth_token():
    print("getting pelm auth token")
    url = '{PELM_API_URL}/auth/refresh'.format(
        PELM_API_URL=app.config.get('PELM_API_URL'),
    )

    data = {
        'email': EMAIL,
        'password': PASSWORD
    }

    response = post(url, data=data)
    response_json = response.json()

    print(response_json)
    return response_json.get('auth_token')


def get_energy_accounts(unique_id, access_token):
    print("get energy accounts")
    url = '{PELM_API_URL}/accounts/get?unique_id={unique_id}'.format(
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
    print(response.content)

    return response.json()['data']

def get_access_token(code):
    print("getting access_token")
    url = '{PELM_API_URL}/auth/token'.format(
        PELM_API_URL=app.config.get('PELM_API_URL')
    )

    data = {
        'grant_type': 'code',
        'code': code,
        'redirect_url': '{}/redirect'.format(app.config.get('STOUT_URL'))
    }


    string = '{id}:{secret}'.format(
        id = app.config.get('PELM_CLIENT_ID'),
        secret=app.config.get('PELM_CLIENT_SECRET')
    )
    encoded_string = base64.b64encode(string.encode())

    headers = {
        'Authorization': f'Basic {encoded_string}'
    }

    response = post(url, data=data, headers=headers)

    print(response)

    print(response.text)

    data = response.json()['data']

    access_token = data['access_token']
    refresh_token = data['refresh_token']

    print(access_token)
    print(refresh_token)

    return access_token



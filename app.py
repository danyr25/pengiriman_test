import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd
import random, string
import admin_page, user_page
import time

#Connect spreadsheet

# Define the scope (permissions) and authenticate
from oauth2client.service_account import ServiceAccountCredentials
import gspread

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

service_account_info = {
  "type": "service_account",
  "project_id": "pengirimannasional-test",
  "private_key_id": "edfb24e2f048cb0849b01523170239875655a530",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQD1d3+dIa3pZVHY\nqdSNr7RmjE2Jj+pFDGNaqYXC/+HEUIYQ3AKNG8P+VpvwejSaEg0MPIrWPrUwlQ/U\nJyc0OnzXX3QvLIflutuR906FO7fM6VL9A67ohoXTI24dAgRsLTGJSbqvXmGJSVSE\nOI5Qp/zMU0XdYeceOpKJRz032hc4h8oGJDl/gXYfUzFhkxJzBbFElfaRrxS3Sizq\nL1C40j9q/cc2tTB9ZlIqa93n7E4b43ecO4ea1aAJIbjAL162onGwYZSv+6H7pZgC\nVmv/TUjjeD62gvaBH7PKninN5ywa2kG/EOrX7+0umlktroA+PHv6f/+ioiEQ/RD+\nyBstfmdLAgMBAAECggEAC0eL9ij7iFuPCME5Eq+tvv6Ye4dA8R5SHHLowh6m/bHj\njzfE6D4L4g6RyNmcvC2zKspHaPPluI9I9Gs+KnC7ltv8h0RpFD3jZBA0q/ukBQb9\nuMGoEmhIEv0wTKXwlRX4jkH0kaVpHvlfKFo+8+bcP3leHv+mMqXnYOaEoiHj6kWA\nESi4hvka+pszo8vtO9ZLYlxYiula14rTxB/MiEl3+7ktUxIm7G5fOoZulJjw3YF8\neIePCOPwL9XhEFD4H+JB75qiYHNpvJMyWdMIV7uXUkg84/Epm53RfnlERJpjXIb0\n2xvWZBOt5yMpyNiTvgxIf2jOBSlXlRzUa1yjxApYfQKBgQD+Q+Iba7pM5joodQG5\nJkPQdZhLikdaWq5BX7udh8/uZpB6Kk5lD+cN/OJsViIq0IF7aJAs6tYnuE1MIOz3\n7hokEVUlNhSyU6JF0SPReDF6dfzMxF906z8AIbOXxGhcy67SfXcdz0laDYQQOkhg\nKfBZfG0yDFpnZe9am+gbPr2QlwKBgQD3JD9WwsEsDYQflCeDDv88F+hhxepnySYz\ndhZOUqEhRO8acqri1xgC2779RtqMJ9y86ZU0T5oMrErOR3Gg0DxSZLo8H9rDn5pX\n1+hAGYokNgKB3pUdS6FG3jGdvJfDM/C0UbxbQjHcdrn5NoYqZaW6jfGy2uSV+AkI\nyOECTCrBbQKBgFzGljUdLMAsbWIft35AWRQyJFzD2t88IUMXVFTZnmRFpkf9Mdes\nYsl20YNoNlVa+TP3ZkwNcBDULdguV2jrxzwL2v6V6h1baOWCt0gSTDN7478vlAkM\nYVOB+I7TCqV5aJPDVfhZj1E9h0eIjKoSA3ITdaCCY2ZBCoIMSzfNv8uHAoGAMW1D\naaOrpJbTbMlhmZl/PFJ/vEYr2jPlevdMAMAPz6qMs1ppiNKBz9iI+viXrt4uDG4e\n1AZzhcNTdqvdMs9SsRvKD0pDo0ohQR5CKcex1AolODn+0owUpiq7+5MDOxwBMN8D\n77BubmwkR447CPGpUoUe6KlUfBXOIL6kGaSIDIUCgYBjBhlBWUPfcboJU5NmyVC2\ndJuId2FFUjZ0cR0fdPjjsV24k92j3ziYhWE6AHT/t+zCyuGzybnRPynA8fKIhYPH\nLrt6jqGNsR5Mqc7c2Aj/vtxHqoluBwfQqWm+jkSOcnGiBVPlet80ZVFV+V/cDzC6\nHuSyaH9FUmrt8Khbp/ikHw==\n-----END PRIVATE KEY-----\n",
  "client_email": "webapp-pengiriman-crud@pengirimannasional-test.iam.gserviceaccount.com",
  "client_id": "103467583507156164729",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/webapp-pengiriman-crud%40pengirimannasional-test.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
client = gspread.authorize(creds)

#Open all table then convert to dataframe
user_sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1mUbmJGAEABhCqjfH7F2Jzb5JkhMSfucl2uVTiLV7Jls/edit?gid=0#gid=0').sheet1
user_table = user_sheet.get_all_values()
df_user = pd.DataFrame(user_table[1:], columns=user_table[0])

#All function goes here

def GenerateToken(length=6):          #Generate random token (for reset password)
       return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def NewUser(name, usr, password):     #Create new user
     name_check = df_user["Name"] == name
     i, j = UserCheck(usr)

     if name_check.any():
          idx = df_user.index[df_user['Name'] == name][0]
          cells_update = [
               gspread.Cell(idx+2, 2, usr),
               gspread.Cell(idx+2, 3, password),
               gspread.Cell(idx+2, 4, 'User')
          ]
          user_sheet.update_cells(cells_update)
          return 'Account Created'
     else:
          user_sheet.append_row([name, usr, password, 'User'])
          return 'Account Created'

def TokenReq(usr):                    #Create new token in database
     i, j = UserCheck(usr)

     if not i:
          return 'Invalid Username', None
     else:
          idx = df_user.index[df_user['User'] == j][0]
          token = GenerateToken()
          user_sheet.update_cell(idx+2,5,token)
          return 'Token Requested', token

def ResetPassword(usr, token, newpassword, sys_token): #Reset password verification and overwrite in database
     i, j = UserCheck(usr)

     if not i:
          return 'Username already exist'

     idx = df_user.index[df_user['User'] == j][0]
     token_data = df_user.loc[df_user['User'] == j, 'Reset Token'].iloc[0]

     if token == token_data:
          user_sheet.update_cell(idx+2,3,newpassword)
          return 'Success'
     elif token == sys_token:
          user_sheet.update_cell(idx+2,3,newpassword)
          return 'Success'
     else:
          return 'Invalid Token'

def UserCheck(usr):                 #Check if user already created
     user_check = df_user["User"] == usr
     return user_check.any(), usr

def LoginCheck(usr,password):       #Login and assign give role of account
     i, j = UserCheck(usr)

     if not i:
          return False, False, None

     pass_check = df_user.loc[df_user['User'] == j, 'Password'].iloc[0]
     role_check = df_user.loc[df_user['User'] == j, 'Role'].iloc[0]

     if pass_check == password:
          return True, True, role_check
     else:
          return True, False, None

@st.dialog("Sign Up", width='small')              #Dialog for sign up
def SignUp():
     name_su = st.selectbox(
          'Select your name',
          df_user['Name'][:245].tolist(),
          index=None,
          placeholder="Select your name or add a new one",
          accept_new_options=True
     )
     user_su = st.text_input("Username", key="new_username", placeholder="Username", autocomplete='off')
     pass_su = st.text_input("Password", type="password", key="new_password", placeholder="Password", autocomplete='off')
     repass_su = st.text_input("Confirm Password", type="password", key="new_password_confirm", placeholder="Re-enter Your Password", autocomplete='off')

     if repass_su != '':
          if pass_su != repass_su:
               st.error('Password doesn\'t match. Please re-check it.')

     if st.button("Sign Up", type='primary', width='stretch'):
          i, j = UserCheck(user_su)

          if name_su == '' or user_su == '' or pass_su == '' or repass_su == '':
               st.warning("Please fill all fields")
          elif i:
               st.error("Username already exist")
          else:
               check_status = NewUser(name_su, user_su, pass_su)
               st.success(check_status)
               time.sleep(1)
               st.rerun()

@st.dialog("Forgot Password", width='small')          #Dialog for forgot password
def ForgotPassword():
     user_fp = st.text_input("Username", key="fp_username", placeholder="Username", autocomplete='off')

     token_req_left, token_req_right = st.columns([2.25,1], border=False, gap='small', vertical_alignment='bottom')
     
     token_fp = token_req_left.text_input("Token", key="fp_token", placeholder="Token", autocomplete='off')
     
     if token_req_right.button("Request Token", type='secondary', width='stretch', help='Klik untuk mendapatkan token, lalu email ke tim Centro Custody HO (dany.rahman@bfi.co.id)'):
          if user_fp == '':
               st.toast("Please fill username first")
          else:
               status, st.session_state.new_token = TokenReq(user_fp)
               st.toast(status)
          
     pass_fp = st.text_input("Password", type="password", key="fp_password", placeholder="Enter your new password", autocomplete='off')
     repass_fp = st.text_input("Confirm Password", type="password", key="fp_password_confirm", placeholder="Re-enter Your Password", autocomplete='off')
     
     if repass_fp != '':
          if pass_fp != repass_fp:
               st.error('Password doesn\'t match. Please re-check it.')
     
     if st.button("Reset Password", type='primary', width='stretch'):
          if user_fp == '' or token_fp == '' or pass_fp == '' or repass_fp == '':
               st.warning("Please fill all fields")
          else:
               check_status = ResetPassword(user_fp, token_fp, pass_fp, st.session_state.new_token)
               if check_status == 'Success':
                    st.success("Password Reset Successful. Please login with your new password")
                    st.session_state.new_token = None
                    time.sleep(3)
                    st.rerun()
               else:
                    st.error(check_status)

#End of function

# ------------- Streamlit App ----------------

#Set session state
if 'role' not in st.session_state:
     st.session_state['role'] = None
     st.session_state['user_key'] = None
     st.session_state['profile_name'] = None

if 'new_token' not in st.session_state:
     st.session_state['new_token'] = None

if st.session_state['role'] == None: #Redirect to login page

     #Set page config & title
     st.set_page_config(page_title="Pengiriman Nasional", page_icon=":fire:", layout="centered")

     leftcol_title, middlecol_title, rightcol_title = st.columns([1,11,1], border=False, gap=None)

     middlecol_title.title('App Pengiriman Nasional :truck:', anchor=False)

     leftcol_subtitle, middlecol_subtitle, rightcol_subtitle = st.columns([1,1.1,1], border=False, gap=None)

     middlecol_subtitle.header('Login Page', anchor=False)
     
     #Login Form
     user_input_login = st.text_input("Username", key="ulogin", placeholder="Username")
     password_input_login = st.text_input("Password", type="password", key="plogin", placeholder="Password", autocomplete='off')

     underform_left, underform_right = st.columns([2.8,1], border=False, gap='small', vertical_alignment='center')

     su_container = underform_right.container(horizontal=True, border=False, horizontal_alignment='center')

     if su_container.button("Sign Up", type='secondary', width='stretch'):
          SignUp()

     forgot_container = st.container(horizontal=True, border=False, horizontal_alignment='center')

     if forgot_container.button("Forgot your password?", type='tertiary', width='stretch'):
          ForgotPassword()     #Call dialog

     notif_container = st.container(horizontal=True, border=False, horizontal_alignment='center')

     if underform_left.button("Login", type='primary', width='stretch'):
          if user_input_login == '' or password_input_login == '':
               notif_container.warning("Please fill all fields")
          else:
               i, j, k = LoginCheck(user_input_login, password_input_login)

               if not i:
                    notif_container.error("Invalid Username")
               else:
                    if not j:
                         notif_container.error("Invalid Password")
                    if i and j:
                         login_name = df_user.loc[df_user['User'] == user_input_login, 'Name'].iloc[0]
                         st.session_state['role'] = k
                         st.session_state['user_key'] = user_input_login
                         st.session_state['profile_name'] = login_name
                         notif_container.success("Login Successful as " + login_name)
                         st.rerun()

     st.write(st.session_state)

if st.session_state['role'] == 'Admin':     #Redirect to admin page
     admin_page.show()

if st.session_state['role'] == 'User':     #Redirect to user page
     user_page.show()

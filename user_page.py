import streamlit as st
from streamlit_option_menu import option_menu
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import time
import datetime
from zoneinfo import ZoneInfo
import uuid

#Connect spreadsheet

# Define the scope (permissions) and authenticate
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("pengirimannasional-test-edfb24e2f048.json", scope)
client = gspread.authorize(creds)

#Open all table then convert to dataframe
user_sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1mUbmJGAEABhCqjfH7F2Jzb5JkhMSfucl2uVTiLV7Jls/edit?gid=0#gid=0').sheet1
user_table = user_sheet.get_all_values()
df_user = pd.DataFrame(user_table[1:], columns=user_table[0])

data_sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/10BlL266KaE2zQ3lq_4mMlxVEA__gaDGHI0_hHdILlCo/edit?gid=0#gid=0').sheet1
data_table = data_sheet.get_all_values()
df_data = pd.DataFrame(data_table[1:], columns=data_table[0])

#Function goes here
def AddDataSingle(data_table, data_sheet, send_from, send_to, agreement_no, no_custody, send_type, awb_no, send_date, send_doc, desc):
     last_row_index = len(data_table)
     now = datetime.datetime.now(ZoneInfo("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M:%S")
     user_update = st.session_state['user_key']
     send_date = send_date.strftime("%m/%d/%Y")
     
     requests = [
          {
               "range": f"A{last_row_index + 1}",
               "values": [[now]]
          },
          {
               "range": f"C{last_row_index + 1}:I{last_row_index + 1}",
               "values": [[send_from, send_to, agreement_no, no_custody, send_type, awb_no, send_date]]
          },
          {
               "range": f"P{last_row_index + 1}:S{last_row_index + 1}",
               "values": [[send_doc, desc, user_update, user_update + '_' + str(uuid.uuid4())[:8]]]
          }
     ]
     
     if last_row_index + 1 > data_sheet.row_count:
          data_sheet.add_rows(1)
          data_sheet.batch_update(requests, value_input_option="USER_ENTERED")
     else:
          data_sheet.batch_update(requests, value_input_option="USER_ENTERED")

def AddDataBatch(data_table, data_sheet, uploaded_file):
     last_row_index = len(data_sheet.get_all_values())
     last_uploaded_row_index = len(uploaded_file)
     now = datetime.datetime.now(ZoneInfo("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M:%S")
     user_update = st.session_state['user_key']
     user_name = st.session_state['profile_name']
     
     uploaded_file["Tanggal Pengiriman"] = uploaded_file["Tanggal Pengiriman"].dt.strftime("%m/%d/%Y")
     uploaded_file["Nomor AWB"] = uploaded_file["Nomor AWB"].str.replace("#", "", regex=False)
     
     values_block1 = [[now] for _ in range(len(uploaded_file))]
     values_block2 = uploaded_file[["Tujuan Pengiriman", "Nomor Kontrak", "Nomor Custody", "Jenis Pengiriman", "Nomor AWB", "Tanggal Pengiriman"]].values.tolist()
     values_block2 = [[user_name] + row for row in values_block2]  # add origin place
     values_block3 = uploaded_file[["Dokumen yang Dikirimkan", "Keterangan"]].values.tolist()
     values_block3 = [row + [user_update] + [user_update + '_' + str(uuid.uuid4())[:8]] for row in values_block3]  # add fixed username

     requests = [
          {
               "range": f"A{last_row_index + 1}:A{last_row_index + last_uploaded_row_index}",
               "values": values_block1
          },
          {
               "range": f"C{last_row_index + 1}:I{last_row_index + last_uploaded_row_index}",
               "values": values_block2
          },
          {
               "range": f"P{last_row_index + 1}:S{last_row_index + last_uploaded_row_index}",
               "values": values_block3
          }
     ]

     if last_row_index + last_uploaded_row_index > data_sheet.row_count:
          data_sheet.add_rows(last_uploaded_row_index)
          data_sheet.batch_update(requests, value_input_option="USER_ENTERED")
     else:
          data_sheet.batch_update(requests, value_input_option="USER_ENTERED")

def ViewData(df_data, search_agreement, search_awb, search_origin, search_destination, search_type, search_send_doc, search_date_range, search_jne_status):
     IsEmpty = False
     df_data = df_data[['sent_from', 'sent_to', 'agreement_no', 'send_type', 'awb_no', 'send_date_opc', 'delivery_status', 'last_tracking_status', 'last_tracking_date','send_doc', 'desc','link']]

     if search_agreement != '':
          df_data = df_data[df_data['agreement_no'].str.contains(search_agreement, case=False, na=False)]
          if df_data.empty:
               IsEmpty = True
     if search_awb != '':
          df_data = df_data[df_data['awb_no'].str.contains(search_awb, case=False, na=False)]
          if df_data.empty:
               IsEmpty = True
     if search_origin != []:
          df_data = df_data[df_data['sent_from'].isin(search_origin)]
          if df_data.empty:
               IsEmpty = True
     if search_destination != []:
          df_data = df_data[df_data['sent_to'].isin(search_destination)]
          if df_data.empty:
               IsEmpty = True
     if search_type != []:
          df_data = df_data[df_data['send_type'].isin(search_type)]
          if df_data.empty:
               IsEmpty = True
     if search_send_doc != []:
          df_data = df_data[df_data['send_doc'].isin(search_send_doc)]
          if df_data.empty:
               IsEmpty = True
     if search_date_range != []:
          df_data = df_data[(df_data['send_date_opc'] >= search_date_range[0].strftime("%m/%d/%Y")) & (df_data['send_date_opc'] <= search_date_range[1].strftime("%m/%d/%Y"))]
          if df_data.empty:
               IsEmpty = True
     if search_jne_status != []:
          df_data = df_data[df_data['delivery_status'].isin(search_jne_status)]
          if df_data.empty:
               IsEmpty = True

     df_data = df_data[['sent_from', 'sent_to', 'agreement_no', 'send_type', 'awb_no', 'send_date_opc', 'last_tracking_date', 'last_tracking_status', 'send_doc', 'desc','link']]
     
     df_data = df_data.rename(columns={'sent_from': 'Cabang Pengirim', 'sent_to': 'Cabang Tujuan', 'agreement_no': 'No. Kontrak', 'send_type': 'Jenis Pengiriman', 
                                        'awb_no': 'No. AWB', 'send_date_opc': 'Tanggal Pengiriman', 'last_tracking_status': 'Status Terakhir', 'last_tracking_date': 'Tanggal Status Terakhir',
                                        'send_doc': 'Isi Paket Pengiriman', 'desc': 'Deskripsi', 'link': 'Link Tracking'}
                              )     
                            
     return df_data, IsEmpty

@st.dialog("Ganti Password", width='small')          #Dialog for change password
def ChangePassword():
     st.write("This is change password dialog")

@st.dialog('Konfirmasi Perubahan Data', width='large')
def ConfirmEditData(changed_rows):
     st.write("This is confirmation dialog")
     
     st.dataframe(
          changed_rows,
          column_config={
               "Hapus Data": st.column_config.CheckboxColumn(
                    "Hapus",
                    help="Centang untuk menghapus data",
                    default=False,
                    width='small',
                    pinned=True
               ),
               "Edit Data": st.column_config.CheckboxColumn(
                    "Edit",
                    help="Centang untuk mengedit data",
                    default=False,
                    width='small',
                    pinned=True
               ),
          },
          hide_index=True,
          column_order=['Edit Data', 'Hapus Data','Cabang Pengirim', 'Cabang Tujuan', 'No. Kontrak', 'No. Custody', 'Jenis Pengiriman', 'No. AWB', 'Tanggal Pengiriman', 'Isi Paket Pengiriman', 'Deskripsi']
     )
     
     if st.button(":material/save: Simpan Perubahan", type='primary', width='stretch'):
          st.success("Perubahan berhasil disimpan")


#End of function
# ------------- Streamlit App ----------------
          
def show():

     st.set_page_config(page_title="Pengiriman Nasional", page_icon=":fire:", layout="wide", initial_sidebar_state='auto', menu_items={'Get Help': 'https://www.extremelycoolapp.com/help', 'Report a bug': "https://www.extremelycoolapp.com/bug", 'About':'TESTING'})
     #st.logo('https://www.bfi.co.id/wp-content/uploads/2021/09/bfi-logo.png')
     
     with st.sidebar:

          #img_col1, img_col2, img_col3 = st.columns([1,10,1], border=False, gap=None)

          #img_col2.image('ProfilePicture.png', use_container_width='auto', width=150)

          st.markdown(
              f"""
              <div style="text-align: center;">
                  <h3>Hello,<br>{st.session_state['profile_name']}</h3>
              </div>
              """,
              unsafe_allow_html=True
          )
          
          selected4 = option_menu(None, ["Home", "Input Data", "Edit Data", "View Data"], 
               icons=['house', 'upload', 'pencil-square', "list-task"], key='menu')

          if st.button("Ganti Password", type='secondary', width='stretch', icon=':material/manage_accounts:'):
               ChangePassword()
          
          if st.button("Logout", type='primary', width='stretch', icon=':material/logout:'):
               st.session_state['role'] = None
               st.session_state['user_key'] = None
               st.session_state['profile_name'] = None
               st.rerun()

     #st.title('This is the user page')

     if st.session_state['menu'] == 'Home' or st.session_state['menu'] == None:
          st.write('This is Home Page')

     if st.session_state['menu'] == 'Input Data':

          if 'clearcolumn' not in st.session_state:
               st.session_state['clearcolumn'] = False

          if 'uploadcount' not in st.session_state:
               st.session_state['uploadcount'] = 0

          if st.session_state['clearcolumn']:
               #st.session_state.send_from = None
               st.session_state.send_to = None
               st.session_state.agreement_no = None
               st.session_state.no_custody = None
               st.session_state.send_type = None
               st.session_state.awb_no = None
               #st.session_state.send_date = None
               st.session_state.send_doc = None
               st.session_state.desc = None
               st.session_state['clearcolumn'] = False
          
          single_input, batch_input = st.tabs(['Single Input', 'Batch Input'])

          with single_input:
          
               col1, col2 = st.columns([1,1], border=False, gap='small', vertical_alignment='center')
               col3, col4 = st.columns([1,1], border=False, gap='small', vertical_alignment='center')
               col5, col6 = st.columns([1,1], border=False, gap='small', vertical_alignment='center')
               col7, col8 = st.columns([1,1], border=False, gap='small', vertical_alignment='top')
               cont1 = st.container(horizontal=True, border=False, horizontal_alignment='center')
               container1 = st.container(horizontal=True, border=False, horizontal_alignment='center')

               branch_list = df_user['Name'][:245].tolist() + ['UDIN SEDUNIA']
               if st.session_state['profile_name'] in branch_list:
                    branch_idx = branch_list.index(st.session_state['profile_name'])
               else:
                    branch_idx = None
               
               send_from = col1.selectbox(
                    'Cabang Pengirim*',
                    branch_list,
                    index=branch_idx,
                    placeholder="Pilih atau tambahkan cabang",
                    accept_new_options=True,
                    key = 'send_from',
               )
               send_to = col2.selectbox(
                    'Cabang Tujuan*',
                    branch_list,
                    index=None,
                    placeholder="Pilih atau tambahkan cabang",
                    accept_new_options=True,
                    key = 'send_to'
               )
               agreement_no = col3.text_input("No. Kontrak*", key="agreement_no", placeholder="No. Kontrak", autocomplete='off')
               no_custody = col4.text_input("No. Custody", key="no_custody", placeholder="No. Custody", autocomplete='off')
               send_type = col5.selectbox(
                    'Jenis Pengiriman*',
                    ['EKSPEDISI', 'MESSENGER'],
                    index=None,
                    placeholder="Pilih jenis pengiriman",
                    key = 'send_type'
               )
     
               if send_type == 'EKSPEDISI':
                    ekspedisi_flag = False
               else:
                    ekspedisi_flag = True
               
               awb_no = col6.text_input("No. AWB*", key="awb_no", placeholder="No. AWB", autocomplete='off', disabled=ekspedisi_flag, help='No. AWB wajib diisi jika jenis pengiriman adalah "EKSPEDISI"')
               send_date = col7.date_input("Tanggal Pengiriman*", key="send_date", format="DD/MM/YYYY", value='today', min_value='2025-01-01' ,max_value='today')
               send_doc = col8.selectbox(
                    'Dokumen yang Dikirim*',
                    ['ASSET', 'PPK', 'ASSET & PPK', 'BAST RELEASE', 'OTHERS'],
                    index=None,
                    placeholder="Pilih dokumen yang dikirim",
                    key = 'send_doc',
                    help = '"ASSET" mengacu pada BPKB, Invoice, SHGB, dan dokumen lainnya yang berkaitan dengan asset yang dikirimkan. Jika "OTHERS" dipilih, mohon untuk mengisi deskripsi dokumen yang dikirimkan pada kolom "Deskripsi" di bawah'
               )
               desc = cont1.text_area("Deskripsi*", key="desc", placeholder="Deskripsi", height=100)

               if container1.button("Submit", type='primary', width='stretch', key='submit_single'):
                    if send_type == 'Ekspedisi':
                         if send_from == '' or send_to == '' or agreement_no == '' or awb_no == '' or send_date == '' or send_doc == '' or desc == '':
                              st.error("Mohon untuk mengisi semua kolom")
                         else:
                              AddDataSingle(data_table, data_sheet, send_from, send_to, agreement_no, no_custody, send_type, awb_no, send_date, send_doc, desc)
                              st.success("Data berhasil disimpan")
                              time.sleep(1)
                              st.session_state['clearcolumn'] = True
                              st.rerun()
                    else:
                         if send_from == '' or send_to == '' or agreement_no == '' or send_type == '' or send_date == '' or send_doc == '' or desc == '':
                              st.error("Mohon untuk mengisi semua kolom")
                         else:
                              AddDataSingle(data_table, data_sheet, send_from, send_to, agreement_no, no_custody, send_type, awb_no, send_date, send_doc, desc)
                              st.success("Data berhasil disimpan")
                              time.sleep(1)
                              st.session_state['clearcolumn'] = True
                              st.rerun()
          with batch_input:
               
               #col_batch1, col_batch2 = st.columns([6,1], border=False, gap='small', vertical_alignment='center')
               st.session_state['uploaded_file'] = None
               
               st.write('Gunakan template di bawah ini untuk menginput data secara batch')
               
               with open("Template Report Pengiriman.xlsx", "rb") as file:
                    st.download_button(
                         label="Download Template Report",
                         data=file,
                         file_name="Template Report Pengiriman.xlsx",
                         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                         on_click='ignore',
                         icon=':material/download:',
                         type='secondary',
                         width='stretch'
                   )
                    
               #st.write('*) Pastikan template diisi dengan benar sebelum diupload agar data tersimpan dengan benar')
               st.divider()
               
               uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx'], accept_multiple_files=False, key=f"uploader_{st.session_state.uploadcount}")
               if uploaded_file is not None:
                    st.write('Preview '+ uploaded_file.name)
                    df = pd.read_excel(uploaded_file)
                    st.write(df.head(10))
                    
                    if st.button("Submit Data", type='primary', width='stretch', key='submit_batch'):
                         AddDataBatch(data_table, data_sheet, df)
                         st.success("Data berhasil disimpan")
                         time.sleep(5)
                         st.session_state.uploadcount += 1
                         st.rerun()
                    
     if st.session_state['menu'] == 'Edit Data':

          button_container = st.container(horizontal=True, border=False, horizontal_alignment='left')

          df_edit_data = df_data[df_data['user_create']==st.session_state['user_key']]
          df_edit_data['send_date_opc'] = pd.to_datetime(df_edit_data['send_date_opc'], format='%m/%d/%Y')
          df_edit_data = df_edit_data[['sent_from', 'sent_to', 'agreement_no', 'no_custody', 'send_type', 'awb_no', 'send_date_opc', 'send_doc', 'desc', 'row_uid']]
          df_edit_data = df_edit_data.rename(columns={'sent_from': 'Cabang Pengirim', 'sent_to': 'Cabang Tujuan', 'agreement_no': 'No. Kontrak', 'no_custody': 'No. Custody','send_type': 'Jenis Pengiriman', 
                                                  'awb_no': 'No. AWB', 'send_date_opc': 'Tanggal Pengiriman', 'send_doc': 'Isi Paket Pengiriman', 'desc': 'Deskripsi'}
                                        )
          df_edit_data['Hapus Data'] = False
          df_edit_data['Edit Data'] = False
          df_edit_data = df_edit_data.set_index('row_uid')

          st.session_state['edit_data'] = df_edit_data
          
          edited_data = st.data_editor(
               st.session_state['edit_data'],
               hide_index=True,
               column_order=['Edit Data', 'Hapus Data','Cabang Pengirim', 'Cabang Tujuan', 'No. Kontrak', 'No. Custody', 'Jenis Pengiriman', 'No. AWB', 'Tanggal Pengiriman', 'Isi Paket Pengiriman', 'Deskripsi'],
               column_config={
                    "Hapus Data": st.column_config.CheckboxColumn(
                         "Hapus",
                         help="Centang untuk menghapus data",
                         default=False,
                         width='small',
                         pinned=True
                    ),
                    "Edit Data": st.column_config.CheckboxColumn(
                         "Edit",
                         help="Centang untuk mengedit data",
                         default=False,
                         width='small',
                         pinned=True
                    ),
                    'Jenis Pengiriman': st.column_config.SelectboxColumn(
                         "Jenis Pengiriman",
                         options=['EKSPEDISI', 'MESSENGER'],
                         required=True
                    ),
                    'Tanggal Pengiriman': st.column_config.DateColumn(
                         "Tanggal Pengiriman",
                         format="MM/DD/YYYY",
                         required=True
                    ),
                    'Isi Paket Pengiriman': st.column_config.SelectboxColumn(
                         "Isi Paket Pengiriman",
                         options=['ASSET', 'PPK', 'ASSET & PPK', 'BAST RELEASE', 'OTHERS'],
                         required=True
                    )
               }
          )

          diff_mask = ~edited_data.eq(df_edit_data).all(axis=1)
          changed_rows = edited_data[diff_mask]
          #st.write(changed_rows)
          
          if button_container.button(":material/save: Simpan Perubahan", type='primary', width='content', key='submit_edit'):
               ConfirmEditData(changed_rows)

          if button_container.button(":material/delete: Reset Perubahan", type='secondary', width='content', key='reset_edit'):
               st.rerun()
          
          st.write(st.session_state)
     if st.session_state['menu'] == 'View Data':

          filter_col1, filter_col2, filter_col3 = st.columns([1,1,1], border=False, gap= 'small', vertical_alignment='center')
          filter_col4, filter_col5 = st.columns([1,1], border=False, gap= 'small', vertical_alignment='center')
          filter_col6, filter_col7, filter_col8 = st.columns([3,6,3], border=False, gap= 'medium', vertical_alignment='center')

          
          list_origin = list(set(df_data['sent_from']))
          list_destination = list(set(df_data['sent_to']))
          list_origin.sort()
          list_destination.sort()

          search_agreement = filter_col1.text_input("No. Kontrak", key="search_agreement", placeholder="No. Kontrak", autocomplete='off')

          search_awb = filter_col2.text_input("No. AWB", key="search_awb", placeholder="No. AWB", autocomplete='off')
          
          search_origin = filter_col4.multiselect(
               'Cabang Pengirim',
               list_origin,
               key = 'search_origin',
               placeholder="Pilih cabang pengirim",
               default=st.session_state['profile_name']
          )

          search_destination = filter_col5.multiselect(
               'Cabang Tujuan',
               list_destination,
               key = 'search_destination',
               placeholder="Pilih cabang tujuan",
               default=None
          )

          search_type = filter_col6.pills(
               'Jenis Pengiriman',
               ['EKSPEDISI', 'MESSENGER'],
               key = 'search_type',
               selection_mode='multi',
               default=['EKSPEDISI', 'MESSENGER'],
               width='content'
          )

          search_send_doc = filter_col7.pills(
               'Isi Paket Pengiriman',
               ['ASSET', 'PPK', 'ASSET & PPK', 'BAST RELEASE', 'OTHERS'],
               key = 'search_send_doc',
               selection_mode='multi',
               default=['ASSET', 'PPK', 'ASSET & PPK', 'BAST RELEASE', 'OTHERS'],
               width='content'
          )

          search_jne_status = filter_col8.pills(
               'Status Pengiriman',
               ['ON PROCESS', 'DELIVERED'],
               key = 'search_jne_status',
               selection_mode='multi',
               default=['ON PROCESS'],
               width='content'
          )
          
          today_default = datetime.date.today()
          previous_month = today_default.month - 1 if today_default.month > 1 else 12
          previous_year = today_default.year if today_default.month > 1 else today_default.year - 1
          start_default = datetime.date(previous_year, previous_month, today_default.day)
          default_range = [start_default,today_default]

          search_date_range = filter_col3.date_input("Tanggal Pengiriman*", key="search_date_range", format="DD/MM/YYYY", value=default_range, min_value='2025-01-01' ,max_value='today')
          
          try:
               data_view, isempty = ViewData(df_data, search_agreement, search_awb, search_origin, search_destination, search_type, search_send_doc, search_date_range, search_jne_status)

               if isempty:
                    st.warning('Data tidak ditemukan')
               else:
                    st.dataframe(
                         data_view,
                         hide_index=True,
                         on_select='ignore',
                         height=550,
                         width='stretch',
                         column_config={
                              "Link Tracking": st.column_config.LinkColumn(
                                   "Tracking",
                                   help="Klik untuk melihat tracking pengiriman",
                                   display_text=":material/open_in_new:",
                                   width='small'
                              )
                         }
                    )

          except Exception:
               st.stop()
          
     #st.write(st.session_state)
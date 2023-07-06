import pandas as pd
from bs4 import BeautifulSoup

def login(page, mf_id, mf_pass):
    MF_EMAIL_SIGN_IN_URL="https://id.moneyforward.com/sign_in/email"
    page.goto(MF_EMAIL_SIGN_IN_URL) 
    # Fill in the email field
    page.fill('#mfid_user\\[email\\]', mf_id)
    # Click the submit button
    page.click('#submitto')
    # Wait for navigation (optional, depending on the page)
    #page.wait_for_load_state('networkidle')
    # Fill in the password field
    page.fill('#mfid_user\\[password\\]', mf_pass) 
    # Click the submit (sign in) button
    page.click('#submitto')
    # Wait for navigation (optional, depending on the page)
    page.wait_for_load_state('networkidle')
    # Go to the MoneyForward Sign In page
    MF_SIGN_IN_URL="https://moneyforward.com/sign_in/"
    page.goto(MF_SIGN_IN_URL)
    # Wait for navigation (optional, depending on the page)
    page.wait_for_load_state('networkidle')
    # Click the submit (Use this account) button
    page.click('#submitto')
    # retuen the page instance
    return page

def delete_all_cash_deposit(page):
    # Handle dialog (popup)　表示されるダイアログを自動的に承認（OKボタンを押す）する。
    page.once("dialog", lambda dialog: dialog.accept())

    # Click all delete buttons(削除ボタンがなくなるまで削除ボタンをクリックし続ける)
    while True:
        # Find all delete buttons within the specified table
        delete_buttons = page.query_selector_all('.table.table-bordered.table-depo .btn-asset-action[data-method="delete"]')

        # If no more delete buttons, break the loop
        if not delete_buttons:
            break

        # Click the first delete button
        delete_buttons[0].click()
        page.wait_for_timeout(3000)

        # Wait for navigation (optional, depending on the page)
        page.wait_for_load_state('networkidle')

def get_mf_cash_deposit(page):
    df = get_data_from_mf_table(page, 'table-depo')
    # '種類・名称'列を'currency'列にリネーム
    if '種類・名称' in df.columns:
        df = df.rename(columns={'種類・名称': 'currency'})
    else:
        df['currency'] = None
    # '残高'列を'value'列にリネーム
    if '残高' in df.columns:
        df = df.rename(columns={'残高': 'value_JPY'})
        # 'value'列について、カンマと「円」を取り除き、intにする。
        df['value_JPY'] = df['value_JPY'].str.replace(",", "").str.replace("円", "").astype(int)
    else:
        df['value_JPY'] = None
    #'asset_id'列を作成
    df['asset_id'] = None
    # 行ごとにループし、webの表からasset_idを取得し代入する
    for index, row in df.iterrows():
        df.loc[index, 'asset_id'] = get_asset_id_from_mf_table(page, 'table-depo', row['row_no_in_mf_table'])
    return df

def get_mf_equity(page):
    df = get_data_from_mf_table(page, 'table-eq')
    # '銘柄コード'列を'symbol'列にリネーム
    if '銘柄コード' in df.columns:
        df = df.rename(columns={'銘柄コード': 'symbol'})
        df['symbol'] = df['銘柄名'].str.split('|').str[0]
    else:
        #dfに"symbol"列を追加する
        df['symbol'] = None
    # '評価額'列を'value'列にリネーム
    if '評価額' in df.columns:
        df = df.rename(columns={'評価額': 'value_JPY'})
        # 'value'列について、カンマと「円」を取り除き、intにする。
        df['value_JPY'] = df['value_JPY'].str.replace(",", "").str.replace("円", "").astype(int)
    else:
        #dfに"value_JPY"列を追加する
        df['value_JPY'] = None
    #'asset_id'列を作成, webの表からasset_idを取得し代入する
    df['asset_id'] = None
    for index, row in df.iterrows():
        df.loc[index, 'asset_id'] = get_asset_id_from_mf_table(page, 'table-eq', row['row_no_in_mf_table'])
    return df

def get_data_from_mf_table(page, table_type):
    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')
    #tableのclass IDを設定
    class_id = f'table table-bordered {table_type}'
    table = soup.find('table', class_=class_id)
    if table is None:
        # テーブルが存在しない場合は空のdfを返す
        df = pd.DataFrame()
        df['row_no_in_mf_table'] = None
        return df
    rows = table.find_all('tr')
    headers = [th.text.strip() for th in rows[0].find_all('th')]
    # テーブルの全データを取得
    depo_data = [] #list
    for row in rows[1:]:
        values = [td.text.strip() for td in row.find_all('td')]
        depo_data.append(values)
    # Pandasのデータフレームに変換
    df = pd.DataFrame(depo_data, columns=headers)
    # 'row_no_in_mf_table'列を作成(index + 1)
    df['row_no_in_mf_table'] = df.index + 1
    # 'row_no_in_mf_table'列を先頭に移動
    df = df.reindex(columns=['row_no_in_mf_table'] + list(df.columns[:-1]))
    df = df.drop(['変更', '削除'], axis=1)
    return df

def get_asset_id_from_mf_table(page, table_type, row_no_in_mf_table):
    if table_type == 'table-depo':
        change_btn_column_no = 3
    elif table_type == 'table-eq':
        change_btn_column_no = 11
    else:
        return False
    element_xpath = '//*[@class="table table-bordered {}"]/tbody/tr[{}]/td[{}]/a'.format(table_type, row_no_in_mf_table, change_btn_column_no)
    element = page.query_selector(element_xpath)
    # href属性から目的の文字列を取得し、これをasset_idとする
    href_attribute = element.get_attribute('href')
    asset_id = href_attribute.replace('#modal_asset', '')
    return asset_id

def modify_asset_in_mf(page, table_type, asset_id, asset_name, market_value, cost_amount):
    # Find all delete buttons within the specified table
    modify_buttons = page.query_selector_all(f'.table.table-bordered.{table_type} .btn-asset-action[data-toggle="modal"]')
    # 変更ボタンの中からasset_idを含むボタンを探しクリックする
    for modify_button in modify_buttons:
        href = modify_button.get_attribute('href')
        if asset_id in href:
            modify_button.click() #クリックするとモーダルが現れる
            break
    #以下モーダルにおける操作
    modal_id = f'modal_asset{asset_id}'
    #---資産の名称を変更---
    asset_det_name_textbox_xpath = f'//div[@id="{modal_id}"]//input[@id="user_asset_det_name"]'
    asset_det_name_textbox = page.query_selector(asset_det_name_textbox_xpath)
    asset_det_name_textbox.fill(str(asset_name)[:20]) #20文字までしか入力できないので、最初の20文字を入力する
    #---現在の価値を変更---
    asset_det_value_textbox_xpath = f'//div[@id="{modal_id}"]//input[@id="user_asset_det_value"]'
    asset_det_value_textbox = page.query_selector(asset_det_value_textbox_xpath)
    asset_det_value_textbox.fill(str(market_value)[:12])
    #---購入価格を変更---
    asset_det_entried_price_textbox_xpath = f'//div[@id="{modal_id}"]//input[@id="user_asset_det_entried_price"]'
    asset_det_entried_price_textbox = page.query_selector(asset_det_entried_price_textbox_xpath)
    asset_det_entried_price_textbox.fill(str(cost_amount)[:12])
    #---「この内容で登録」ボタンを押す---
    commit_btn_xpath = f'//div[@id="{modal_id}"]//input[@name="commit"]'
    commit_btn = page.query_selector(commit_btn_xpath)
    commit_btn.click()
    #---モーダルが消えるまで待つ---
    page.wait_for_timeout(3000)
    page.wait_for_load_state('networkidle')
    return True

def create_asset_in_mf(page, asset_type, asset_name, market_value, cost_amount):
    page.get_by_role("button", name="手入力で資産を追加").click()
    page.get_by_role("combobox", name="資産の種類").select_option(str(asset_type))
    page.get_by_label("資産の名称").fill(str(asset_name)[:20])
    page.get_by_label("現在の価値").fill(str(market_value)[:12])
    page.get_by_label("購入価格").fill(str(cost_amount)[:12])
    page.get_by_role("button", name="この内容で登録する").click()
    page.wait_for_timeout(2000)
    page.wait_for_load_state('networkidle')
    return True

def delete_asset_in_mf(page, table_type, asset_id):
    # Handle dialog (popup)　表示されるダイアログを自動的に承認（OKボタンを押す）する。
    page.once("dialog", lambda dialog: dialog.accept())
    # Find all delete buttons within the specified table
    delete_buttons = page.query_selector_all(f'.table.table-bordered.{table_type} .btn-asset-action[data-method="delete"]')
    # 削除ボタンの中からasset_idを含むボタンを探す
    for delete_button in delete_buttons:
        href = delete_button.get_attribute('href')
        if asset_id in href:
            delete_button.click()
            # Wait for 1 sec
            page.wait_for_timeout(1000)
            # Wait for navigation (optional, depending on the page)
            page.wait_for_load_state('networkidle')
            break
    return True

def reflect_to_mf_cash_deposit(page, ib_cash_report):
    # ---pageから「預金・現金・暗号資産」の表を取得する。
    mf_cash_deposit = get_mf_cash_deposit(page)
    #merge(ib_cash_reportとmf_cash_depositを突き合わる、キーはcurrency)
    merged_df = pd.merge(mf_cash_deposit, ib_cash_report, on='currency', how='outer').fillna('NONE')
    # 'Action' 列を追加
    merged_df['Action'] = 'NONE'  # 初期値を設定
    # 条件に基づいて 'Action' 列を更新
    merged_df.loc[(merged_df['row_no_in_mf_table'] != 'NONE') & (merged_df['value_JPY'] != merged_df['endingCash_JPY']), 'Action'] = 'MODIFY'
    merged_df.loc[(merged_df['row_no_in_mf_table'] != 'NONE') & (merged_df['endingCash_JPY'] == 'NONE'), 'Action'] = 'DELETE'
    merged_df.loc[(merged_df['row_no_in_mf_table'] == 'NONE') & (merged_df['endingCash_JPY'] != 'NONE'), 'Action'] = 'ADD'
    #print(merged_df)
    # ---更新を実施---
    df_to_modify = merged_df[(merged_df['Action'] == 'MODIFY')]
    for index, row in df_to_modify.iterrows():
        modify_asset_in_mf(page, 'table-depo', row['asset_id'], row['currency'], int(row['endingCash_JPY']), '')
    # ---削除を実施---
    df_to_delete = merged_df[(merged_df['Action'] == 'DELETE')]
    for index, row in df_to_delete.iterrows():
        delete_asset_in_mf(page, 'table-depo', row['asset_id'])
    # ---追加を実施---
    df_to_add = merged_df[(merged_df['Action'] == 'ADD')]
    for index, row in df_to_add.iterrows():
        create_asset_in_mf(page, '51', row['currency'], int(row['endingCash_JPY']), '')
        #'51'とは「保証金・証拠金」のこと
    return True

def reflect_to_mf_equity(page, ib_open_position):
    # ---pageから「預金・現金・暗号資産」の表を取得する。
    mf_equity = get_mf_equity(page)
    #merge(ib_cash_reportとmf_cash_depositを突き合わる、キーはsymbol)
    merged_df = pd.merge(mf_equity, ib_open_position, on='symbol', how='outer').fillna('NONE')
    # 'Action' 列を追加
    merged_df['Action'] = 'NONE'  # 初期値を設定
    # 条件に基づいて 'Action' 列を更新
    merged_df.loc[(merged_df['row_no_in_mf_table'] != 'NONE') & (merged_df['value_JPY'] != merged_df['positionValue_JPY']), 'Action'] = 'MODIFY'
    merged_df.loc[(merged_df['row_no_in_mf_table'] != 'NONE') & (merged_df['positionValue_JPY'] == 'NONE'), 'Action'] = 'DELETE'
    merged_df.loc[(merged_df['row_no_in_mf_table'] == 'NONE') & (merged_df['positionValue_JPY'] != 'NONE'), 'Action'] = 'ADD'
    #print(merged_df)
    # ---更新を実施---
    df_to_modify = merged_df[(merged_df['Action'] == 'MODIFY')]
    for index, row in df_to_modify.iterrows():
        asset_name_to_input = row['symbol'] + "|" + str(row['position'])
        modify_asset_in_mf(page, 'table-eq', row['asset_id'], asset_name_to_input, int(row['positionValue_JPY']), int(row['costBasisMoney_JPY']))
    # ---削除を実施---
    df_to_delete = merged_df[(merged_df['Action'] == 'DELETE')]
    for index, row in df_to_delete.iterrows():
        delete_asset_in_mf(page, 'table-eq', row['asset_id'])
    # ---追加を実施---
    df_to_add = merged_df[(merged_df['Action'] == 'ADD')]
    for index, row in df_to_add.iterrows():
        asset_name_to_input = row['symbol'] + "|" + str(row['position'])
        if row['currency'] == 'JPY':
            asset_type_to_input = '14' #'14':国内株（日本株）
        elif row['currency'] == 'USD':
            asset_type_to_input = '15' #'15':米国株
        elif row['currency'] == 'CNY' or row['currency'] == 'HKD':
            asset_type_to_input = '16' #'16':中国株
        else:
            asset_type_to_input = '55' #'55':その他外国株
        create_asset_in_mf(page, asset_type_to_input, asset_name_to_input, int(row['positionValue_JPY']), int(row['costBasisMoney_JPY']))
    return True

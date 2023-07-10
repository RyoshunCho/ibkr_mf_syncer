import streamlit as st
from playwright.sync_api import sync_playwright
import ibkr_flex_query_client as ibflex
import moneyforward_processing as mfproc
import utils

def main(MF_EMAIL, MF_PASS, IB_FLEX_QUERY_FOR_MF_ID, IB_FLEX_TOKEN, MF_IB_INSTITUTION_URL):
    # ---GET IB FLEX REPORT---
    ib_cash_report = ibflex.get_ib_flex_report(IB_FLEX_TOKEN, IB_FLEX_QUERY_FOR_MF_ID, 'CashReport')
    ib_cash_report = utils.add_value_jpy(ib_cash_report, 'endingCash', 'endingCash_JPY') # 現金残高を日本円に変換
    ib_open_position = ibflex.get_ib_flex_report(IB_FLEX_TOKEN, IB_FLEX_QUERY_FOR_MF_ID, 'OpenPositions')
    ib_open_position = utils.add_value_jpy(ib_open_position, 'costBasisMoney', 'costBasisMoney_JPY') # 取得金額を日本円に変換
    ib_open_position = utils.add_value_jpy(ib_open_position, 'positionValue', 'positionValue_JPY') # 現在価値を日本円に変換
    with sync_playwright() as playwright:
        # Open a new browser context
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            #Change user agent 以下のようにuser_agentを偽造しないと、MoneyForwardのログイン画面が表示されないため。
            user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
        )
        page = context.new_page()
        # Handle dialog (popup)　表示されるダイアログを自動的に承認（OKボタンを押す）する。
        page.once("dialog", lambda dialog: dialog.accept())
        # ---MoneyForward Me Login---
        page = mfproc.login(page, MF_EMAIL, MF_PASS)
        # ---MoneyForward上で手動登録したIBKRのページに遷移---
        page.goto(MF_IB_INSTITUTION_URL)
        page.wait_for_load_state('networkidle')
        # ---取得したIB FLEX REPORTをMoneyForward MEに反映する---
        mfproc.reflect_to_mf_cash_deposit(page, ib_cash_report)
        mfproc.reflect_to_mf_equity(page, ib_open_position)
        # Close browser context
        context.close()
        browser.close()

def app():
    st.title('IBKR to MoneyForward Syncer')

    MF_EMAIL = st.text_input('MF_EMAIL')
    MF_PASS = st.text_input('MF_PASS', type='password')
    IB_FLEX_QUERY_FOR_MF_ID = st.text_input('IB_FLEX_QUERY_FOR_MF_ID')
    IB_FLEX_TOKEN = st.text_input('IB_FLEX_TOKEN', type='password')
    MF_IB_INSTITUTION_URL = st.text_input('MF_IB_INSTITUTION_URL')

    if st.button('Sync'):
        main(MF_EMAIL, MF_PASS, IB_FLEX_QUERY_FOR_MF_ID, IB_FLEX_TOKEN, MF_IB_INSTITUTION_URL)
        st.success('Finished!')

if __name__ == "__main__":
    app()
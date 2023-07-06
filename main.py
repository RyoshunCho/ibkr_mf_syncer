import configparser
from playwright.sync_api import sync_playwright
import ibkr_flex_query_client as ibflex
import moneyforward_processing as mfproc
import utils

def main():
    # ConfigParserオブジェクトを作成してconfig.iniファイルを読み込む
    config = configparser.ConfigParser()
    config.read('config.ini')
    # configのmoneyforwardセクションからemailとpasswordとIBKRのURLを取得する
    MF_EMAIL = config.get('moneyforward', 'email')
    MF_PASS = config.get('moneyforward', 'password')
    MF_IB_INSTITUTION_URL = config.get('moneyforward', 'ib_institution_url')
    # configのibkr_flex_queryセクションからtokenとquery_idを取得する
    IB_FLEX_TOKEN = config.get('ibkr_flex_query', 'token')
    IB_FLEX_QUERY_FOR_MF_ID = config.get('ibkr_flex_query', 'query_id')
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
        
if __name__ == "__main__":
    main()
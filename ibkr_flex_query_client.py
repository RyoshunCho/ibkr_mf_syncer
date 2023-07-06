from ibflex import client
import pandas as pd
import xml.etree.ElementTree as ET

def get_ib_flex_report(ib_flex_token, ib_flex_query_id, report_type):
    # Get the IB FLEX report
    response = client.download(ib_flex_token, ib_flex_query_id)
    xml_string = response.decode('utf-8')
    root = ET.fromstring(xml_string)
    # <CashReport>要素を探索
    report_element = root.find(f'FlexStatements/FlexStatement/{report_type}')
    # データを格納するためのリストを作成
    data_list = []
    def extract_data(element):
        # currencyが"BASE_SUMMARY"の場合は除外する
        if report_type == 'CashReport':
            if element.get('currency') == "BASE_SUMMARY":
                return
        # 株以外のアセットは除外する
        elif report_type == 'OpenPositions':
            if element.get('assetCategory') != "STK":
                return
        else:
            return False
        # データを格納するための辞書
        row = {}
        # 必要な属性のみ辞書に追加
        attributes_to_keep = [
            'accountId',
            'currency',
            'fromDate',
            'toDate',
            'reportDate',
            'endingCash',
            'assetCategory',
            'subCategory',
            'symbol',
            'description',
            'listingExchange',
            'openPrice',
            'costBasisPrice',
            'costBasisMoney',
            'side',
            'positionValue',
            'fifoPnlUnrealized',
            'position'
        ]
        for attr in attributes_to_keep:
            if attr in element.attrib:
                row[attr] = element.attrib[attr]

        # データをリストに追加
        data_list.append(row)
    # CashReportCurrency要素を抽出する関数を呼び出す
    if report_type == 'CashReport':
        for report_element in report_element.findall('CashReportCurrency'):
            extract_data(report_element)
    elif report_type == 'OpenPositions':
        for report_element in report_element.findall('OpenPosition'):
            extract_data(report_element)
    else:
        return False
    # リストからDataFrameを作成
    df = pd.DataFrame(data_list)
    #print(df)
    return df
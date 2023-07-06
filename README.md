# IBKR MF Syncer
Sync the stock portofolio in IBKR to MoneyForward ME.

IBKR MF Syncerは、[Interactive Brokers (IBKR)](https://www.interactivebrokers.com/)の株式のポートフォリオを[MoneyForward ME](https://moneyforward.com/)に同期するPythonスクリプトです。このスクリプトは、IBKRから[Flex Queries](https://www.interactivebrokers.com/en/software/singlefunds/topics/flexqueries.htm#:~:text=Flex%20Queries%20let%20you%20specify,want%20to%20view%20your%20report.)で生成されたxml形式のレポートを取得し、その情報をMoneyForward MEに反映します。

## 制約
- Cash残高と現物株式のみに対応しています。他の商品（債権、投信、先物、CFD、オプション等）には（まだ）対応していません。※手伝ってくれる方募集中です。
- yahoo finance から取得した為替情報を使用して円換算をしているが、あまり正確ではなく、参考程度に。
- Interactive Brokers (IBKR)のFlex web serviceのTokenはいつまでも有効ではないです。有効期間が1年間です。失効したら新に設定が必要です。ご注意を。

## 準備
- IB証券側の準備：
  - IB証券の口座設定で[Flex web serviceを有効化](https://www.ibkrguides.com/brokerportal/flexwebservice.htm#:~:text=To%20enable%20flex%20web%20service,or%20disable%20Flex%20Web%20Service.)しておくこと。
  - 有効にしたら、[Current Token](https://www.ibkrguides.com/clientportal/flex3.htm)をメモること。
  - 1つ[Activity Flex queryを作成](https://www.ibkrguides.com/clientportal/performanceandstatements/activityflex.htm)しておくこと。セクション(Sections)は、以下の２つを選択しておくこと。他のセクションを選択しないこと。
    - (1)オープン・ポジション[(Open Position)](https://ibkrguides.com/reportingreference/reportguide/openpositions_default.htm)
       - オプションは「サマリー」のみ選択。
       - 項目は全ての項目を選択
    - (2)キャッシュ・レポート[(Cash Report)](https://ibkrguides.com/reportingreference/reportguide/cashreport_default.htm)
       - オプションは何も選択しない。
       - 項目は全ての項目を選択
    - 他の設定は全てデフォルトのまま。
    - クエリ名はなんでも良い。
    - 作成後、そのクエリーIDをメモっておくこと。
- MoneyForward ME側の設定：
  - MoneyForward MEで「IB証券」を[(自動取得に対応していない)金融機関(証券)として手動登録](https://support.me.moneyforward.com/hc/ja/articles/900004425703-%E8%87%AA%E5%8B%95%E5%8F%96%E5%BE%97%E3%81%AB%E5%AF%BE%E5%BF%9C%E3%81%97%E3%81%A6%E3%81%84%E3%81%AA%E3%81%84%E9%87%91%E8%9E%8D%E6%A9%9F%E9%96%A2%E3%82%92%E7%99%BB%E9%8C%B2%E3%81%97%E3%81%9F%E3%81%84)しておくこと。
  - [ここ](https://moneyforward.com/accounts/new/manual?category_type=SEC)から登録できます。「金融機関名」はなんでも良いです。 e.g: IBKR
  - 登録したら、[【口座】→【登録済み金融機関】](https://moneyforward.com/accounts)→「手元の現金・資産」のセクションに「IBKR」があるはずです。それをクリック後、URLをメモっておくこと。

## 使い方

1. まず、準備でメモったものを全て`config.ini`に反映し、保存する。
2. 次に、スクリプトを実行します。
```bash
python main.py
```

## ライブラリ

以下のライブラリが必要です。
- configparser
- playwright
- ibflex
- pandas
- BeautifulSoup
- yfinance

以下のコマンドでインストールできます。

```bash
pip install configparser playwright ibflex pandas beautifulsoup4 yfinance
```



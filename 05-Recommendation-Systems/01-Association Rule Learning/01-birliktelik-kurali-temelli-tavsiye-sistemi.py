####################################################################################################
# Birliktelik Kuralı Temelli Tavsiye Sistemi Projesi
####################################################################################################

## Is Problemi
# Sepet asamasindaki kullanicilara urun onerisinde bulunmak


## Veri Seti Hikayesi
# Online Retail II isimli veri seti, 01.12.2009 - 09.12.2011 tarihleri arasinda bir İngiliz perakende sirketi icin yapilmis olan online satislarin kayitlarini iceriyor.
# Bu sirket hediyelik eşya satan bir perakende sirketi. Urunlerin çogu hediyelik eşya. Fakat perakende sirketi çogu müsterisine hediye olarak hediyelik eşya satmaktan ziyade, kendi ürünlerini satmaktan gelir elde ediyor.


## Degiskenler
# InvoiceNo: Fatura numarasi. Her islem icin farkli ve her fatura icin benzersiz. C ile baslayanlar iptal edilen islemleri ifade ediyor.
# StockCode: Urun kodu. Her bir urun icin benzersiz.
# Description: Urun ismi
# Quantity: Urun adedi. Her bir fatura icin pozitif tam sayi.
# InvoiceDate: Fatura tarihi ve saati.
# UnitPrice: Birim fiyat. Sterlin cinsinden.
# CustomerID: Eşsiz müşteri numarası
# Country: Ülke ismi. Müşterinin yaşadığı ülke.


### 1. Veri On Isleme
### 2. ARL Veri Yapisini Hazirlama (Invoice-Prouct Matrix)
### 3. Birliktelik Kuralinin Cikarilmasi
### 4. Calismanin Scriptni Hazirlama
### 5. Sepet Asamasindaki Kullaniciya Urun Onerisinde Bulunmak

#########################################
# 1. Veri On Isleme
#########################################

import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 500)
pd.set_option('display.expand_frame_repr', False)
from mlxtend.frequent_patterns import apriori, association_rules

# Veri setini okuma
df_ = pd.read_excel("online_retail_II.xlsx", sheet_name="Year 2010-2011")

df = df_.copy()

# hata alirsaniz, "pip install openpyxl" komutunu calistirin (terminalde).
# pd.read_excel("online_retail_II.xlsx", sheet_name="Year 2010-2011", engine="openpyxl") seklinde de calistirabilirsiniz.

df.head()

# veri setine ait istatistiksel bilgiler icin
df.describe().T

# veri setinde eksiklik var mi?
df.isnull().sum()

# veri seti sekil bilgisi
df.shape


def retail_data_prep(dataframe):
    dataframe.dropna(inplace=True)
    # iade edilen urunlerin (negatif quantity) silinmesi
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]
    # Quantity degeri 0'dan buyuk olanlarin secilmesi
    dataframe = dataframe[(dataframe['Quantity'] > 0)]
    # Price degeri 0'dan buyuk olanlarin secilmesi
    dataframe = dataframe[(dataframe['Price'] > 0)]
    replace_with_thresholds(dataframe, "Quantity")
    replace_with_thresholds(dataframe, "Price")
    return dataframe

df = retail_data_prep(df)

# aykiri degerler icin fonksiyon
def outlier_thresholds(dataframe, variable):
    quartile1 = dataframe[variable].quantile(0.01)
    quartile3 = dataframe[variable].quantile(0.99)
    interquartile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquartile_range
    low_limit = quartile1 - 1.5 * interquartile_range
    return low_limit, up_limit

def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit

#########################################
# 2. ARL Veri Yapisini Hazirlama (Invoice-Prouct Matrix)
#########################################

df.head()

df_fr = df[df["Country"] == "France"]
df_fr.shape

df_fr.groupby(["Invoice", "Description"]).agg({"Quantity": "sum"}).head(20)

df_fr.groupby(["Invoice", "Description"]).agg({"Quantity": "sum"}).unstack().iloc[0:5, 0:5]

df_fr.groupby(["Invoice", "Description"]).agg({"Quantity": "sum"}).unstack().fillna(0).iloc[0:5, 0:5]

df_fr.groupby(["Invoice", "Description"]).agg({"Quantity": "sum"}).unstack().fillna(0).applymap(lambda x: 1 if x > 0 else 0).iloc[0:5, 0:5]

df_fr.groupby(["Invoice", "StockCode"]).agg({"Quantity": "sum"}).unstack().fillna(0).applymap(lambda x: 1 if x > 0 else 0)

def create_invoice_product_df(dataframe, id=False):
    if id:
        return dataframe.groupby(["Invoice", "StockCode"])["Quantity"].sum().unstack().fillna(0).applymap(
            lambda x: 1 if x > 0 else 0)
    else:
        return dataframe.groupby(["Invoice", "Description"])["Quantity"].sum().unstack().fillna(0).applymap(
            lambda x: 1 if x > 0 else 0)

fr_inv_pro_df = create_invoice_product_df(df_fr)

fr_inv_pro_df = create_invoice_product_df(df_fr, id=True)

def check_id(dataframe, stock_code):
    product_name = dataframe[dataframe["StockCode"] == stock_code][["Description"]].values[0].tolist()
    print(product_name)

check_id(df_fr, 22726)

#########################################
# 3. Birliktelik Kuralinin Cikarilmasi
#########################################

frequent_itemsets = apriori(fr_inv_pro_df, min_support=0.01, use_colnames=True)

frequent_itemsets.sort_values("support", ascending=False)

rules = association_rules(frequent_itemsets, metric="support", min_threshold=0.01)

rules[(rules["support"] > 0.05) & (rules["confidence"] > 0.1) & (rules["lift"] > 5)]

rules[(rules["support"] > 0.05) & (rules["confidence"] > 0.1) & (rules["lift"] > 5)].shape

rules[(rules["support"] > 0.05) & (rules["confidence"] > 0.1) & (rules["lift"] > 5)].sort_values("confidence", ascending=False)

#########################################
# 4. Calismanin Scriptni Hazirlama
#########################################

# aykiri degerler icin fonksiyon
def outlier_thresholds(dataframe, variable):
    quartile1 = dataframe[variable].quantile(0.01)
    quartile3 = dataframe[variable].quantile(0.99)
    interquartile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquartile_range
    low_limit = quartile1 - 1.5 * interquartile_range
    return low_limit, up_limit

def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit

def retail_data_prep(dataframe):
    dataframe.dropna(inplace=True)
    # iade edilen urunlerin (negatif quantity) silinmesi
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]
    # Quantity degeri 0'dan buyuk olanlarin secilmesi
    dataframe = dataframe[(dataframe['Quantity'] > 0)]
    # Price degeri 0'dan buyuk olanlarin secilmesi
    dataframe = dataframe[(dataframe['Price'] > 0)]
    replace_with_thresholds(dataframe, "Quantity")
    replace_with_thresholds(dataframe, "Price")
    return dataframe

def create_invoice_product_df(dataframe, id=False):
    if id:
        return dataframe.groupby(["Invoice", "StockCode"])["Quantity"].sum().unstack().fillna(0).applymap(
            lambda x: 1 if x > 0 else 0)
    else:
        return dataframe.groupby(["Invoice", "Description"])["Quantity"].sum().unstack().fillna(0).applymap(
            lambda x: 1 if x > 0 else 0)

def check_id(dataframe, stock_code):
    product_name = dataframe[dataframe["StockCode"] == stock_code][["Description"]].values[0].tolist()
    print(product_name)

def create_rules(dataframe, id=True, country="France"):
    dataframe = dataframe[dataframe["Country"] == country]
    dataframe = create_invoice_product_df(dataframe, id)
    frequent_itemsets = apriori(dataframe, min_support=0.01, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric="support", min_threshold=0.01)
    return rules


df = df_.copy()

df = retail_data_prep(df)

rules = create_rules(df)

rules[(rules["support"] > 0.05) & (rules["confidence"] > 0.1) & (rules["lift"] > 5)].sort_values("confidence", ascending=False)

#########################################
# 5. Sepet Asamasindaki Kullaniciya Urun Onerisinde Bulunmak
#########################################

# Örnek
# Kullanici ornek urun id: 22492

product_id = 22492
check_id(df, product_id)

sorted_rules = rules.sort_values("lift", ascending=False)

recommendation_list = []

for i , product in enumerate(sorted_rules["antecedents"]):
    for j in list(product):
        if j == product_id:
            recommendation_list.append(list(sorted_rules.iloc[i]["consequents"])[0])

recommendation_list[0:5]

for i in range(5):
    check_id(df, recommendation_list[i])


def arl_recommender(rules_df, product_id, rec_count=1):
    sorted_rules = rules_df.sort_values("lift",ascending=False)
    recommendation_list = []
    for i,product in enumerate(sorted_rules["antecedents"]):
        for j in list(product):
            if j == product_id:
                recommendation_list.append(list(sorted_rules.iloc[i]["consequents"])[0])
    return recommendation_list[0:rec_count]

arl_recommender(rules,22492,1)

arl_recommender(rules,22492,2)

arl_recommender(rules,22492,3)
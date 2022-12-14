####################################################################################################
# CUSTOMER LIFETIME VALUE (MUSTERI YASAM BOYU DEGERI)
####################################################################################################

# 1. Veriyi Hazırlama (Data Preparation)
# 2. Average Order Value (AOV) (average_order_value = total_price / total_transaction)
# 3. Purchase Frequency (PF) (total_transaction / total_number_of_customers)
# 4. Repeat Rate and Churn Rate (RR & CR) (birden fazla alisveris yapanlar / tum musteriler)
# 5. Profit Margin (PM) (profit_margin = total_price * 0.1) # Profit Degisebilir # Profit can be changed
# 6. Customer Value (CV) (customer_value = average_order_value * purchase_frequency)
# 7. Customer Lifetime Value (CLTV) (CLTV = (customer_value / churn_rate) * profit_margin)
# 8. Segmentlerin Olusturulmasi (Segment Creation)
# 9. Tum Islemlerin Fonksiyonlastirilmasi (All Operations in Function)


##############################################
# 1. Veriyi Hazırlama (Data Preparation)
##############################################

# Bir e-ticaret şirketinin müşterilerini RFM analizi ile segmentlere ayırıp,
# bu segmentlere göre pazarlama stratejileri belirlemek istiyor.

# Veri Seti Hikayesi (Story of the Dataset)
# https://archive.ics.uci.edu/ml/datasets/Online+Retail+II

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

import pandas as pd
from sklearn.preprocessing import MinMaxScaler
pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

df_ = pd.read_excel("../online_retail_II.xlsx",sheet_name="Year 2009-2010")

df = df_.copy()

df.head()

df.isnull().sum()

df = df[~df["Invoice"].str.contains("C", na=False)] # C ile baslayanlar iptal edilen islemleri ifade ediyor.
# Bu faturalar quantity ve price degerlerini negatif olarak gosteriyor. O yuzden bu faturalari cikardik.

df.describe().T

df = df[df["Quantity"] > 0] # Quantity degeri negatif olanlari cikardik.

# Eksik değerleri çıkaralım.
df.dropna(inplace=True)

df.describe().T

df['TotalPrice'] = df['Quantity'] * df['Price']

cltv_c = df.groupby('Customer ID').agg({'Invoice': lambda x: x.nunique(), # total_transaction
                                        'Quantity': lambda x: x.sum(), # total_unit
                                        'TotalPrice': lambda x: x.sum()}) # total_price

cltv_c.columns = ['total_transaction', 'total_unit', 'total_price']

##############################################
# 2. Average Order Value (AOV) (average_order_value = total_price / total_transaction)
##############################################

cltv_c.head()

cltv_c["total_price"] / cltv_c["total_transaction"]

# bunu kaydedelim
cltv_c["average_order_value"] = cltv_c["total_price"] / cltv_c["total_transaction"]

##############################################
# 3. Purchase Frequency (PF) (total_transaction / total_number_of_customers)
##############################################

cltv_c.head()

cltv_c.shape[0] # total_number_of_customers 'dır. Çünkü cltv_c, df dataframeninin Customer ID'lerine göre gruplandırılmış halidir.

cltv_c['purschase_frequency'] = cltv_c['total_transaction'] / cltv_c.shape[0]

##############################################
# 4. Repeat Rate and Churn Rate (RR & CR) (birden fazla alisveris yapanlar / tum musteriler)
##############################################

cltv_c.head()

repeat_rate = cltv_c[cltv_c["total_transaction"] > 1].shape[0] / cltv_c.shape[0]

churn_rate = 1 - repeat_rate


##############################################
# 5. Profit Margin (PM) (profit_margin = total_price * 0.1) # Profit Degisebilir # Profit can be changed
##############################################

cltv_c.head()

cltv_c["profit_margin"] = cltv_c["total_price"] * 0.1

##############################################
# 6. Customer Value (CV) (customer_value = average_order_value * purchase_frequency)
##############################################

cltv_c.head()

cltv_c["customer_value"] = cltv_c["average_order_value"] * cltv_c["purschase_frequency"]

##############################################
# 7. Customer Lifetime Value (CLTV) (CLTV = (customer_value / churn_rate) * profit_margin)
##############################################

cltv_c.head()

cltv_c["cltv"] = (cltv_c["customer_value"] / churn_rate) * cltv_c["profit_margin"]

#buyukten kucuge siralayalim
cltv_c.sort_values(by="cltv", ascending=False).head(10)

#istatistiklere bakalim
cltv_c.describe().T

##############################################
# 8. CLTV Skorlari
##############################################

# qcut
cltv_c["segment"] = pd.qcut(cltv_c["cltv"], 4, labels=["D", "C", "B", "A"])

cltv_c.sort_values(by="cltv", ascending=False).head()

cltv_c.groupby("segment").agg({"count","mean","sum"})

#cltv_c.to_csv("cltv_c.csv")

##############################################
# 9. Tum Islemlerin Fonksiyonlastirilmasi (All Operations in Function)
##############################################

def create_cltv_c(dataframe, profit=0.10, csv=False):

    # Veriyi hazirlama
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]
    dataframe = dataframe[dataframe["Quantity"] > 0]
    dataframe.dropna(inplace=True)
    dataframe['TotalPrice'] = dataframe['Quantity'] * dataframe['Price']
    cltv_c = dataframe.groupby('Customer ID').agg({'Invoice': lambda x: x.nunique(), # total_transaction
                                                    'Quantity': lambda x: x.sum(), # total_unit
                                                    'TotalPrice': lambda x: x.sum()}) # total_price
    
    cltv_c.columns = ['total_transaction', 'total_unit', 'total_price']

    # AOV
    cltv_c["avg_order_value"] = cltv_c["total_price"] / cltv_c["total_transaction"]

    # Purchase Frequency
    cltv_c['purchase_frequency'] = cltv_c['total_transaction'] / cltv_c.shape[0]

    # Repeat Rate and Churn Rate
    repeat_rate = cltv_c[cltv_c["total_transaction"] > 1].shape[0] / cltv_c.shape[0]
    churn_rate = 1 - repeat_rate

    # Profit Margin
    cltv_c["profit_margin"] = cltv_c["total_price"] * profit

    # Customer Value
    cltv_c["customer_value"] = cltv_c["avg_order_value"] * cltv_c["purchase_frequency"]

    # Customer Lifetime Value
    cltv_c["cltv"] = (cltv_c["customer_value"] / churn_rate) * cltv_c["profit_margin"]

    # Segment
    cltv_c["segment"] = pd.qcut(cltv_c["cltv"], 4, labels=["D", "C", "B", "A"])

    if csv:
        cltv_c.to_csv("cltv_c.csv")

    return cltv_c


df = df_.copy()

clv = create_cltv_c(df)
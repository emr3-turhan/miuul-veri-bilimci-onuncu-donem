############################################################################################################
# BG-NBD ve Gamma-Gamma ile CLTV Prediction
############################################################################################################

# 1. Verinin hazırlanması (Data Preparation)
# 2. BG-NBD Modeli ile Expected Number of Transactions (Eksik Alışveriş Sayısı Tahmini)
# 3. Gamma-Gamma Modeli ile Expected Average Profit (Eksik Ortalama Kazanç Tahmini)
# 4. BG-NBD ve Gamma-Gamma ile CLTV'nin hesaplanması
# 5. CLTV'nin segmentlerin oluşturulması
# 6. Calismanin Fonsiyonlastirilmasi 

#################################################
# 1. Verinin hazırlanması (Data Preparation)
#################################################

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

import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter
from lifetimes.plotting import plot_period_transactions

pd.set_option('display.max_columns', None)
pd.set_option("display.width", 500)
pd.set_option('display.float_format', lambda x: '%.4f' % x)

from sklearn.preprocessing import MinMaxScaler

def outlier_thresholds(dataframe, variable):
    quartile1 = dataframe[variable].quantile(0.01)
    quartile3 = dataframe[variable].quantile(0.99)
    IQR = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * IQR
    low_limit = quartile1 - 1.5 * IQR
    return low_limit, up_limit

def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit

#################################################
# Veri Setinin Okunması
#################################################

df_ = pd.read_excel("../online_retail_II.xlsx",sheet_name="Year 2010-2011")

df = df_.copy()

df.head()

df.describe().T

df.isnull().sum()

#################################################
# Veri Onisleme
#################################################

df.dropna(inplace=True)
df = df[~df["Invoice"].str.contains("C", na=False)]
df = df[df["Quantity"] > 0]
df = df[df["Price"] > 0]

replace_with_thresholds(df, "Quantity")
replace_with_thresholds(df, "Price")

df.describe().T 

df["TotalPrice"] = df["Quantity"] * df["Price"]

today_date = dt.datetime(2011, 12, 11)

#################################################
# Lifetime Veri Yapısının Hazırlanması
#################################################

# recency: Son satın alma üzerinden geçen zaman. Haftalık (Kullanıcı özelinde)
# T: Müşterinin yaşı. Haftalık. (analiz tarihinden ne kadar süre önce ilk satın alma yapıldı)
# monetary: satın alma başına ortalama kazanç. (Kullanıcı özelinde)

cltv_df = df.groupby('Customer ID').agg({'InvoiceDate': [lambda InvoinceDate: (InvoinceDate.max() - InvoinceDate.min()).days,
                                                         lambda date: (today_date - date.min()).days],
                                            'Invoice': lambda Invoice: Invoice.nunique(),
                                            'TotalPrice': lambda TotalPrice: TotalPrice.sum()})

cltv_df.columns = cltv_df.columns.droplevel(0)

cltv_df.columns = ['recency', 'T', 'frequency', 'monetary']

cltv_df["monetary"] = cltv_df["monetary"] / cltv_df["frequency"]

cltv_df = cltv_df[(cltv_df['frequency'] > 1)]

cltv_df.describe().T

cltv_df["recency"] = cltv_df["recency"] / 7

cltv_df["T"] = cltv_df["T"] / 7


#################################################
# 2. BG-NBD Modelinin Kurulması
#################################################

bgf = BetaGeoFitter(penalizer_coef=0.001)

bgf.fit(cltv_df['frequency'],
        cltv_df['recency'],
        cltv_df['T'])

#################################################
# 1 Hafta içinde en çok satın alma beklediğimiz 10 müşeteri kimdir?
#################################################

bgf.conditional_expected_number_of_purchases_up_to_time(1,
                                                         cltv_df['frequency'],  # müşterinin satın alma sayısı
                                                            cltv_df['recency'],  # müşterinin son satın alma tarihi
                                                            cltv_df['T']).sort_values(ascending=False).head(10)  # müşterinin yaşam süresi

# 1 yerine 4 yazarsak 4 hafta içinde en çok satın alma beklediğimiz musterileri goruruz ve sayilarini
# 1 ay icinde en cok satın alma bekledigimiz 10 musteri
bgf.conditional_expected_number_of_purchases_up_to_time(4,
                                                            cltv_df['frequency'],  # müşterinin satın alma sayısı
                                                            cltv_df['recency'],  # müşterinin son satın alma tarihi
                                                            cltv_df['T']).sort_values(ascending=False).head(10)

# kaydedelim.
cltv_df["expected_purc_1_month"] = bgf.conditional_expected_number_of_purchases_up_to_time(4,
                                                            cltv_df['frequency'],  # müşterinin satın alma sayısı      
                                                            cltv_df['recency'],  # müşterinin son satın alma tarihi
                                                            cltv_df['T'])

cltv_df["expected_purc_3_month"] = bgf.conditional_expected_number_of_purchases_up_to_time(12,
                                                            cltv_df['frequency'],  # müşterinin satın alma sayısı      
                                                            cltv_df['recency'],  # müşterinin son satın alma tarihi
                                                            cltv_df['T'])

# 1 aylik toplam beklenen satın alma sayisi
cltv_df["expected_purc_1_month"].sum()

# biraz çılgınlık yapalım.

# for i in range(1,5,1):
#     print(bgf.conditional_expected_number_of_purchases_up_to_time(i,
#                                                             cltv_df['frequency'],  # müşterinin satın alma sayısı      
#                                                             cltv_df['recency'],  # müşterinin son satın alma tarihi
#                                                             cltv_df['T']).sum())


#################################################
# 3 aylık beklenen satın alma sayısı
#################################################

bgf.conditional_expected_number_of_purchases_up_to_time(4*3,
                                                            cltv_df['frequency'],  # müşterinin satın alma sayısı
                                                            cltv_df['recency'],  # müşterinin son satın alma tarihi
                                                            cltv_df['T']).sum()


#################################################
# Tahmin sonuclarinin degerlendirilmesi
#################################################

plot_period_transactions(bgf)
plt.show()

#################################################
# 3. Gamma-Gamma Modelinin Kurulması
#################################################   
ggf = GammaGammaFitter(penalizer_coef=0.01)
ggf.fit(cltv_df['frequency'], cltv_df['monetary'])

ggf.conditional_expected_average_profit(cltv_df['frequency'],
                                        cltv_df['monetary']).sort_values(ascending=False).head(10)

cltv_df["expected_average_profit"] = ggf.conditional_expected_average_profit(cltv_df['frequency'],
                                                                            cltv_df['monetary'])

cltv_df.sort_values(by="expected_average_profit" ,ascending=False).head(10)

#################################################
# 4. BG-NBD ve Gamma-Gamma Modeli ile CLTV'nin Hesaplanması

# CLTV = Expected Number of Transactions(BG/NBD)* Expected Average Profit(GG)

cltv = ggf.customer_lifetime_value(bgf,
                                    cltv_df['frequency'],
                                    cltv_df['recency'],
                                    cltv_df['T'],
                                    cltv_df['monetary'],
                                    time=3,  # 3 aylık
                                    freq="W",  # T'nin frekans bilgisi (W: haftalık)
                                    discount_rate=0.01)  # haftalık indirim oranı

cltv.head()

cltv = cltv.reset_index()

cltv_final = cltv_df.merge(cltv, on="Customer ID", how="left")

cltv_final.sort_values(by="clv", ascending=False).head(10)

# normalde receny'si dusuk olan musterinin daha degerleri olmasi gerekir ama buy till you die modeline gore eger musteri
# churn olamdiysa satin alma olasilgi yukseliyor der. Yani eger musteri sadiksa ve bir suredir satin alma gerceklestirmiyorsa
# yakin zamanda satin alma olasiligi yukseliyor demektir. Geliyor demektir potansiyeli artar.

# Aslinda musteriyi degerli yapan tek bir kistas yoktur musteriyi degerli yapan bir cok kriter vardir. CLTV ile bu durumlari
# uygun bir sekilde degerlendirebiliriz.

#################################################
# 5. CLTV Segmentlerinin Oluşturulması
#################################################

cltv_final["segment"] = pd.qcut(cltv_final["clv"], 4, labels=["D", "C", "B", "A"])

cltv_final.sort_values(by="clv",ascending=False).head(50)

cltv_final.groupby("segment").agg({"count", "mean", "sum"})

# Hesapladiktan sonrasi... Yeni musteri getirme sonucu kazanclar ve mevcut musterilerin kazanclari bunlara bagli 
# strateji belirleme


#################################################
# 6. Tum sureci fonksiyonlastirma
#################################################

def create_cltv_p(dataframe,month = 3):
    # 1. Veri On Isleme

    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]
    dataframe = dataframe[dataframe["Quantity"] > 0]
    dataframe = dataframe[dataframe["Price"] > 0]
    replace_with_thresholds(dataframe, "Quantity")
    replace_with_thresholds(dataframe, "Price")
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]
    today_date = dt.datetime(2011, 12, 11)

    cltv_df = dataframe.groupby('Customer ID').agg({'InvoiceDate': [lambda InvoiceDate: (InvoiceDate.max() - InvoiceDate.min()).days,
                                                                lambda InvoiceDate: (today_date - InvoiceDate.min()).days], 
                                            'Invoice': lambda Invoice: Invoice.nunique(),
                                            'TotalPrice': lambda TotalPrice: TotalPrice.sum()})
    
    cltv_df.columns = cltv_df.columns.droplevel(0)
    cltv_df.columns = ['recency', 'T', 'frequency', 'monetary']
    cltv_df["monetary"] = cltv_df["monetary"] / cltv_df["frequency"]
    cltv_df = cltv_df[cltv_df["frequency"] > 1]
    cltv_df["recency"] = cltv_df["recency"] / 7
    cltv_df["T"] = cltv_df["T"] / 7

    # 2. BG-NBD Modelinin Kurulması
    bgf = BetaGeoFitter(penalizer_coef=0.001)
    bgf.fit(cltv_df['frequency'],
            cltv_df['recency'],
            cltv_df['T'])

    cltv_df["expected_purc_1_week"] = bgf.predict(1,
                                                cltv_df['frequency'],
                                                cltv_df['recency'],
                                                cltv_df['T'])


    cltv_df["expected_purc_1_month"] = bgf.predict(4,
                                                cltv_df['frequency'],
                                                cltv_df['recency'],
                                                cltv_df['T'])


    cltv_df["expected_purc_3_month"] = bgf.predict(12,
                                                cltv_df['frequency'],
                                                cltv_df['recency'],
                                                cltv_df['T'])


    # 3. Gamma-Gamma Modelinin Kurulması

    ggf = GammaGammaFitter(penalizer_coef=0.01)

    ggf.fit(cltv_df['frequency'], cltv_df['monetary'])

    cltv_df["expected_average_profit"] = ggf.conditional_expected_average_profit(cltv_df['frequency'],
                                                                                cltv_df['monetary'])
                                    
    # 4. BG-NBD ve Gamma-Gamma Modeli ile CLTV'nin Hesaplanması
    cltv = ggf.customer_lifetime_value(bgf,
                                    cltv_df['frequency'],   
                                    cltv_df['recency'],
                                    cltv_df['T'],
                                    cltv_df['monetary'],
                                    time=month,  # 3 aylık
                                    freq="W",  # T'nin frekans bilgisi (W: haftalık)
                                    discount_rate=0.01)  # haftalık indirim oranı (kayip gibi dusunulebilir)
    
    cltv = cltv.reset_index()
    cltv_final = cltv_df.merge(cltv, on="Customer ID", how="left")
    cltv_final["segment"] = pd.qcut(cltv_final["clv"], 4, labels=["D", "C", "B", "A"])

    return cltv_final


# Şimdi fonksiyonu deneyelim.

df = df_.copy()

cltv_final2 = create_cltv_p(df)

cltv_final2.to_csv("cltv_prediction.csv")





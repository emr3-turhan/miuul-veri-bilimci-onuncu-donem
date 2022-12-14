############################################################################
# RFM ile Müşteri Segmentasyonu (Customer Segmentation with RFM)
############################################################################

# 1. İş Problemi (Business Problem)
# 2. Veriyi Anlama (Data Understanding)
# 3. Veriyi Hazırlama (Data Preparation)
# 4. RFM Metriklerinin Hesaplanması (Calculating RFM Metrics)
# 5. RFM Skorlarının Hesaplanması (Calculating RFM Scores)
# 6. RFM Segmentlerinin Oluşturulması ve Analiz Edilmesi (Creating RFM Segments and Analyzing)
# 7. Tüm Sürecin Fonksiyonlaştırılması (Functionlization of the Entire Process)





##########################################
# 1. İş Problemi (Business Problem)
##########################################

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


############################################
# 2. Veriyi Anlama (Data Understanding)
############################################

import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)
# pd.set_option('display.max_rows', None)

df_ = pd.read_excel("../online_retail_II.xlsx",sheet_name="Year 2009-2010")

df = df_.copy()

df.head()

df.shape

df.isnull().sum()

# CustomerID ve Description değişkenlerinde eksik gözlemler var.
# CustomerID'si eksik olan gözlemleri çıkaracağız.

# essiz urun sayisi
df["Description"].nunique()
df["StockCode"].nunique()

df["Description"].value_counts().head()

# En cok siparis edilen urunler

df.groupby("Description").agg({"Quantity":"sum"}).sort_values("Quantity",ascending=False).head()

# Toplam Ucret icin "TotalPrice" degiskeni olusturuyoruz.
df["TotalPrice"] = df["Quantity"] * df["Price"]

# Fatura basina toplam ucret
df.groupby("Invoice").agg({"TotalPrice":"sum"}).head()

############################################
# 3. Veriyi Hazırlama (Data Preparation)
############################################

df.shape

# Eksik gözlemleri çıkarıyoruz.
df.dropna(inplace=True)

# Outlier baskilama yapmak RFM'de etkili sonuc vermez. Zaten Maksimum 5 degeri alacaklar baskilamadan sonra da bu degeri alirlar.

# Iadeler yuzunden negatif degerler var. Iadeleri cikaralim.
df = df[~df["Invoice"].str.contains("C", na=False)] # na=False: NaN degerlerini cikarmasin.


############################################
# 4. RFM Metriklerinin Hesaplanması (Calculating RFM Metrics)
############################################

# Recency: Son alisveris tarihi
# Frequency: Toplam alisveris sayisi
# Monetary: Toplam harcama

# Analiz tarihi olarak 2010-12-11 tarihini alalim.
today_date = dt.datetime(2010,12,11)

# RFM icin CustomerID ye gore groupby islemi yapilir.

rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                        'Invoice': lambda Invoice: Invoice.nunique(),
                                        'TotalPrice': lambda TotalPrice: TotalPrice.sum()}) 


rfm.head()

rfm.columns = ['recency', 'frequency', 'monetary']

# Istatistiksel ozetler
rfm.describe().T

rfm = rfm[(rfm['monetary'] > 0)]

rfm.shape

############################################
# 5. RFM Skorlarının Hesaplanması (Calculating RFM Scores)
############################################

#  Recency degerini 1-5 arasinda skorlara cevirelim. # 5 düşük recency değerini, 1 yüksek recency değerini ifade etsin.
rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])

#  Frequency degerini 1-5 arasinda skorlara cevirelim. # 1 düşük frequency değerini, 5 yüksek frequency değerini ifade etsin.
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

# Monetary degerini 1-5 arasinda skorlara cevirelim. # 1 düşük monetary değerini, 5 yüksek monetary değerini ifade etsin.
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))
# Monetary degeri RFM skorlarinin hesaplanmasinda kullanilmayacak.

# RFM_SCORE degiskeni string tipindedir.

# Sampiyon Musteriler
rfm[rfm["RFM_SCORE"]=="55"].head()

############################################
# 6. RFM Segmentlerinin Oluşturulması (Creating RFM Segments)
############################################

# Regex ile RFM_SCORE
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)

rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

# cant_loose 
rfm[rfm["segment"]=="cant_loose"].head()
rfm[rfm["segment"]=="cant_loose"].index

new_df = pd.DataFrame()

new_df["new_customer_id"] = rfm[rfm["segment"]=="new_customers"].index

new_df["new_customer_id"] = new_df["new_customer_id"].astype(int)

new_df.to_csv("new_customers.csv") 

############################################
# 7. Tum Surecin Fonskiyonlaştırılması (Functionlizing the Entire Process)
############################################

def create_rfm(dataframe, csv = False):

    # VERIYI HAZIRLAMA
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)] # na=False: NaN degerlerini cikarmasin.

    # RFM METRIKLERININ HESAPLANMASI
    today_date = dt.datetime(2011,12,11)
    rfm = dataframe.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                                'Invoice': lambda Invoice: Invoice.nunique(),
                                                'TotalPrice': lambda TotalPrice: TotalPrice.sum()})
    rfm.columns = ['recency', 'frequency', 'monetary']
    rfm = rfm[(rfm['monetary'] > 0)]

    # RFM SKORLARININ HESAPLANMASI
    rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

    # cltv_df skorlari kategorik degere donusturulup df e eklendi.
    rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))

    # SEGMENTLERIN ISIMLENDIRILMESI
    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }

    rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
    rfm = rfm[["recency", "frequency", "monetary", "segment"]]
    rfm.index = rfm.index.astype(int)

    if csv:
        rfm.to_csv("rfm.csv")

    return rfm


df = df_.copy()
rfm_new = create_rfm(df,csv=True)

# Tum bu islemlerin duzenli olarak yapilip aksiyonlar belirlenmelidir. Segment degisimlerine gore aksiyonlar degerledirilmelidir.


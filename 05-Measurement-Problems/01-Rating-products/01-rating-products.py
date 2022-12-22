####################################################################################################
# Rating products
####################################################################################################

# - Averege
# - Time-Based Weighted Average
# - User-Based Weighted Average
# - Weighted Average


########################################################
# Uygulama: Kullanıcı ve Zaman Ağırlıklı Kurs Puanı Hesaplama
########################################################

import pandas as pd
import math
import scipy.stats as st
from sklearn.preprocessing import MinMaxScaler

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 500)
pd.set_option('display.expand_frame_repr', False)
pd.set_option("display.float_format", lambda x: "%.5f" % x)

# (50+ Saat) Python ile Veri Bilimi ve Makine Öğrenmesi
# Puan: 4.8
# Toplam Puan: 4611
# Yaklaşık Sayısal Karşılıkları: 4358, 922, 184, 46, 6

df = pd.read_csv("../course_reviews.csv")
df.head()

df.shape

# Rating dagilimi 
df["Rating"].value_counts()

df["Questions Asked"].value_counts()

# Sorulan soru kırılımında olusan puan
df.groupby("Questions Asked").agg({'Questions Asked': 'count', 'Rating': 'mean'})

###########################
# Average
###########################

# Ortalama puan
df["Rating"].mean()
# Puani sadece ortalama ile bulmaya calisirsak urune ait son trendleri kaciriyor oluyoruz yani urun hakkinda belki de son donemde cok iyi yorumlar
# gelmis olabilir ama ortalama puan alirsak bu yorumlari kaciriyor oluyoruz. Puani daha yuksek veya dusuk gozukebilir. Urunle ilgili memnuniyet
# tren kacar. Bu treni kacirmamak icin time based weighted average kullanabiliriz.

###########################
# Time-Based Weighted Average
###########################
# Puan Zamanlarina Gore Ağırlıklı Ortalama

df.head()
df.info()

df["Timestamp"] = pd.to_datetime(df["Timestamp"]) # Timestamp sutununu datetime formatina ceviriyoruz

current_date = pd.to_datetime("2021-02-10 0:0:0") # Simdiki tarihi belirliyoruz

df["days"] = (current_date - df["Timestamp"]).dt.days # Simdiki tarihten timestamp sutunundaki tarihe kadar olan gun sayisini hesapliyoruz

df[df["days"] <= 30].count() # 30 gun icindeki yorum sayisi

# Son 30 gundekı yorumlarin ortalama puanı
df[df["days"] <= 30]["Rating"].mean()

# ya da loc kullanarak
df.loc[df["days"] <= 30, "Rating"].mean()

# son 30 ile 90 gun arasındaki yorumlarin ortalama puanı loc kullanarak
df.loc[(df["days"] > 30) & (df["days"] <= 90), "Rating"].mean()

# Zaman agırlıklı ortalama bulalım

df.loc[df["days"] <= 30, "Rating"].mean() * 28 / 100 + \
    df.loc[(df["days"]  > 30) & (df["days"] <= 90), "Rating"].mean() * 26 / 100 + \
        df.loc[(df["days"]  > 90) & (df["days"] <= 180), "Rating"].mean() * 24 / 100 +\
            df.loc[df["days"]  > 180, "Rating"].mean() * 22 / 100

# Hadi bunu fonksiyon haline getirelim

def time_based_weighted_average(dataframe, w1=28, w2= 26, w3=24, w4=22):
    return dataframe.loc[dataframe["days"] <= 30, "Rating"].mean() * w1 / 100 + \
        dataframe.loc[(dataframe["days"]  > 30) & (dataframe["days"] <= 90), "Rating"].mean() * w2 / 100 + \
            dataframe.loc[(dataframe["days"]  > 90) & (dataframe["days"] <= 180), "Rating"].mean() * w3 / 100 +\
                dataframe.loc[dataframe["days"]  > 180, "Rating"].mean() * w4 / 100

time_based_weighted_average(df)

time_based_weighted_average(df, w1=30, w2= 26, w3=22, w4=22)

# Gercekten bunlari konusmak zorundamiyiz? EVETT !!! Virgulden sonraki basamaklar cok onemli!

###########################
# User-Based Weighted Average
###########################

df.head()

# Kullanicnin yaptigi yorumlarin degeri ne olmali? Hangi kullanicinin yorumlarinin daha degerli oldugunu nasil belirleyebiliriz?

df.groupby("Progress").agg({"Rating": "mean"})

df.loc[df["Progress"] <= 10, "Rating"].mean() * 22 / 100 + \
    df.loc[(df["Progress"]  > 10) & (df["Progress"] <= 45), "Rating"].mean() * 24 / 100 + \
        df.loc[(df["Progress"]  > 45) & (df["Progress"] <= 75), "Rating"].mean() * 26 / 100 + \
            df.loc[df["Progress"]  > 75, "Rating"].mean() * 28 / 100

# Hadi bunu fonksiyon haline getirelim

def user_based_weighted_average(dataframe, w1=22, w2= 24, w3=26, w4=28):
    return dataframe.loc[dataframe["Progress"] <= 10, "Rating"].mean() * w1 / 100 + \
        dataframe.loc[(dataframe["Progress"]  > 10) & (dataframe["Progress"] <= 45), "Rating"].mean() * w2 / 100 + \
            dataframe.loc[(dataframe["Progress"]  > 45) & (dataframe["Progress"] <= 75), "Rating"].mean() * w3 / 100 + \
                dataframe.loc[dataframe["Progress"]  > 75, "Rating"].mean() * w4 / 100


user_based_weighted_average(df,20,24,26,30)

###########################
# Weighted Average
###########################

# Kullanici ve zaman agirlikli ortalama

def course_weighted_rating(dataframe, time_w=50,user_w=50):
    return time_based_weighted_average(dataframe) * time_w / 100 + user_based_weighted_average(dataframe) * user_w / 100

course_weighted_rating(df)

course_weighted_rating(df, time_w=40, user_w=60)

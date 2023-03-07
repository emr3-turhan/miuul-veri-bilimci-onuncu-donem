####################################################################################################
# Sorting products
####################################################################################################

##################################################
# Uygulama: Kurs Sıralama
##################################################

import pandas as pd
from sklearn.preprocessing import MinMaxScaler
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option("display.float_format", lambda x: "%.5f" % x)

df = pd.read_csv("../product_sorting.csv")
print(df.shape)

df.head(10)

# Ratinglere gore sıralarsak yeterli olur mu? Kısmen...

##################################################
# Ratinglere Gore Sıralama
##################################################

df.sort_values("rating", ascending=False).head(20)

##################################################
# Yorum Sayisina ya da Satin Alma Sayisina Gore Sıralama
##################################################

df.sort_values("purchase_count", ascending=False).head(20)

df.sort_values("commment_count", ascending=False).head(20)

##################################################
# Puana, Yoruma ve Satın Alma Sayısına Gore Sıralama
##################################################

# Olceklemek lazım çünkü bu degerlerin arasında cok fark var

df["purchase_count_scaled"] = MinMaxScaler(feature_range=(1,5)).fit(df[["purchase_count"]]).transform(df[["purchase_count"]])

# fit ve transform arasındaki fark nedir?
# fit: veriyi ölçeklendirir
# transform: ölçeklendirilmiş veriyi dönüştürür

df["commment_count_scaled"] = MinMaxScaler(feature_range=(1,5)).fit(df[["commment_count"]]).transform(df[["commment_count"]])

df.describe().T

(df["commment_count_scaled"] * 32 / 100 +
 df["purchase_count_scaled"] * 26 / 100 +
 df["rating"] * 42 / 100)
# BUNLAR PUAN(RATING) DEGIL !!! BUNLAR SKORDUR(SCORE).

# Fonksiyon olusturalim

def weighted_sorting_score(dataframe, w1=32, w2=26,w3=42):
    return (dataframe["commment_count_scaled"] * w1 / 100 +
            dataframe["purchase_count_scaled"] * w2 / 100 +
            dataframe["rating"] * w3 / 100)

df["weighted_sorting_score"] = weighted_sorting_score(df)

df.sort_values("weighted_sorting_score", ascending=False).head(20)

df[df["course_name"].str.contains("Veri Bilimi")].sort_values("weighted_sorting_score", ascending=False).head(20)

##################################################
# Bayesian Average Rating Score
##################################################

# Sorting Products with 5 Star Rated
# Sortıng Products According to Distribution of 5 Star Rating

# Gerekli kütüphaneleri import edelim
# Lets import necessary libraries
import math
import scipy.stats as st

def bayesian_average_rating(n, confidence=0.95):
    if sum(n) == 0:
        return 0
    K = len(n)
    z = st.norm.ppf(1 - (1 - confidence) / 2)
    N = sum(n)
    first_part = 0.0
    second_part = 0.0
    for k, n_k in enumerate(n):
        first_part += (k + 1) * (n[k] + 1) / (N + K)
        second_part += (k + 1) * (k + 1) * (n[k] + 1) / (N + K)
    score = first_part - z * math.sqrt((second_part - first_part * first_part) / (N + K + 1))
    return score 

df.head()

df["bar_score"] = df.apply(lambda x: bayesian_average_rating(x[["1_point", "2_point", "3_point", "4_point", "5_point"]]), axis=1)


df.sort_values("weighted_sorting_score", ascending=False).head(20)

df.sort_values("bar_score", ascending=False).head(20)

##################################################
# Hybrid Sorting: BAR Score + Diger Faktorler
##################################################

# Rating Products
# - Average
# - Time-Based Weighted Average
# - USer-Based Weighted Average
# - Weighted Rating
# - Bayesian Average Rating Score

# Sorting Products
# - Sorting by Rating
# - Sorting by Comment Count or Purchase Count
# - Sorting by Rating, Comment and Purchase
# - Sorting by Bayesian Average Rating Score (Sorting Products with 5 Star Rated)
# - Hybrid Sorting: BAR Score + Diger Faktorler

def hybrid_sorting_score(dataframe, bar_w = 60, wss_w= 40):
    bar_score = dataframe.apply(lambda x: bayesian_average_rating(x[["1_point", 
                                                                     "2_point", 
                                                                     "3_point", 
                                                                     "4_point", 
                                                                     "5_point"]]), axis=1)
    
    wss_score = weighted_sorting_score(dataframe)

    return bar_score * bar_w / 100 + wss_score * wss_w / 100

df["hybrid_sorting_score"] = hybrid_sorting_score(df)

df.sort_values("hybrid_sorting_score", ascending=False).head(20)


##################################################
# Uygulama: IMDB Movie Scoring and Sorting
##################################################

import pandas as pd
import math
import scipy.stats as st
pd.set_option('display.max_columns', None)
pd.set_option("display.expand_frame_repr", False)
pd.set_option("display.float_format", lambda x: "%.5f" % x)

df = pd.read_csv("../movies_metadata.csv", 
                 low_memory=False) # DtypeWarning kapatmak icin

df = df[["title","vote_average","vote_count"]]

df.head()
df.shape

##################################
# Vote Average'a Gore Sıralama
##################################

df.sort_values("vote_average", ascending=False).head(20)

df["vote_count"].describe([0.10, 0.25, 0.50, 0.70,0.80, 0.90, 0.95, 0.99]).T

df[df["vote_count"] > 400].sort_values("vote_average", ascending=False).head(20) # Yeterli degil

# Vote Countlari min-max scale edelim (1-10)

df["vote_count_score"] = MinMaxScaler(feature_range=(1,10)).fit(df[["vote_count"]]).transform(df[["vote_count"]])

# Şimdi bunları çarparak yeni bir score elde edelim.

df["average_count_score"] = df["vote_average"] * df["vote_count_score"]

# Siralama

df.sort_values("average_count_score", ascending=False).head(20)# Bu da yeterli degil

##################################################
# IMDB Agirlikli Derecelendirme (Weighted Rating)
##################################################

# IMDB'nin 2015 yilinda kullandigi agirlikli derecelendirme formulu

# weighted rating = (v / (v+M) * r) + (M / (v+M) * C)

# r = vote_average
# v = vote_count
# M = minimum votes required to be listed in the top 250
# C = the mean vote across the whole report

# Film 1:
# r = 8
# M = 500
# v = 1000

# (1000 / (1000+500)) * 8 = 5.33


# Film 2:
# r = 8
# M = 500
# v = 3000

# (3000 / (3000+500)) * 8 = 6.85

# Birinci bolum
# (3000 / (3000+500)) * 8 = 6.85

# Ikinci bolum
# (500 / (3000+500)) * 7 = 1

# Toplam = 7.85

M = 2500
C = df["vote_average"].mean()

def weighted_rating(r, v, M, C):
    return (v / (v+M) * r) + (M / (v+M) * C)


# Deadpool filmi icin agirlikli derecelendirme
weighted_rating(7.4, 11444, M, C) # 7.08

# Inception filmi icin agirlikli derecelendirme
weighted_rating(8.1, 14075, M, C) # 7.72

# The Shawshank Redemption filmi icin agirlikli derecelendirme
weighted_rating(8.5, 8358, M, C) # 7.83


# Bunu butun filmler icin uygulayalim.
df["weighted_rating"] = weighted_rating(df["vote_average"], df["vote_count"], M, C)

# Siralama
df.sort_values("weighted_rating", ascending=False).head(20)

# Bu da yeterli degil x2

##################################################
# Bayesian Average Rating Score
##################################################

# Yeni IMDB Yontemi Denemesi

def bayesian_average_rating(n, confidence=0.95):
    if sum(n) == 0:
        return 0
    K = len(n)
    z = st.norm.ppf(1 - (1 - confidence) / 2)
    N = sum(n)
    first_part = 0.0
    second_part = 0.0
    for k, n_k in enumerate(n):
        first_part += (k + 1) * (n[k] + 1) / (N + K)
        second_part += (k + 1) * (k + 1) * (n[k] + 1) / (N + K)
    score = first_part - z * math.sqrt((second_part - first_part * first_part) / (N + K + 1))
    return score 

df = pd.read_csv("../imdb_ratings.csv")
df = df.iloc[0:, 1:]

df.head()

df["bar_score"] = df.apply(lambda x: bayesian_average_rating(x[["one", 
                                                                "two", 
                                                                "three", 
                                                                "four", 
                                                                "five",
                                                                "six", 
                                                                "seven", 
                                                                "eight", 
                                                                "nine", 
                                                                "ten"]]), axis=1)

df.sort_values("bar_score", ascending=False).head(20)















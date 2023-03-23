###############################################################
# Proje: Item-Based Tavsiye Sistemi
###############################################################

##############################################
# Is Bilgisi
##############################################

# Online bir film izleme platformu is birlikci filtreleme yontemi
# ile bir oneri sistemi gelistirmek istemektedir.

# Icerik temelli oneri sistemlerini deneyen sirket toplulugun
# kannalerini barindiracak sekilde oneriler gelistirmek istemektedir.

# Kullanicilar bir film begendiginde o film ile benzer begenilme
# oruntusune sahip olan diger filmler onerilmek istenmektedir.

##############################################
# Veri Seti Hikayesi
##############################################

# Veri seti MoviesLens tarafindan saglanmistir. Icerisinide filmler

# ve filmlere verilen puanlari barindirmaktadir.

# Vero seti yaklasik 27000 film icin yaklasik 20000000 derecelendirme
# icermektedir.

##############################################
# Degiskenler
##############################################

# movie.csv
# movieId: Film id'si (Conncected to movieId in rating.csv)
# title: Film adi

# rating.csv
# userId: Kullanici id'si
# movieId: Film id'si (Connected to movieId in movie.csv)
# rating: Kullanici tarafindan verilen puan
# timestamp: Puan verme zaman


##############################################
# Item-Based Collaborative Filtering
##############################################

# Veri seti: https://grouplens.org/datasets/movielens/

# Adim 1 : Veri setinin hazirlanmasi
# Adim 2 : User Movie Df'sinin olusturulmasi
# Adim 3 : Item-Based Film Onerilerinin Yapilmasi
# Adim 4 : Calisma Scriptinin Oluşturulması

##############################################
# Adim 1 : Veri setinin hazirlanmasi
##############################################

import pandas as pd
pd.set_option('display.max_columns', 500)

movie = pd.read_csv('../movie_lens_dataset/movie.csv')
rating = pd.read_csv('../movie_lens_dataset/ratings.csv')
df = movie.merge(rating, how='left', on='movieId')
df.head()

##############################################
# Adim 2 : User Movie Df'sinin olusturulmasi
##############################################

df.head()
df.shape

df["title"].value_counts().head()

comment_counts = pd.DataFrame(df["title"].value_counts())

#comment_counts["title"] <= 1000

rare_movies = comment_counts[comment_counts["title"] <= 1000].index

common_movies = df[~df["title"].isin(rare_movies)]

common_movies.shape

common_movies["title"].nunique()
df["title"].nunique()

user_movie_df = common_movies.pivot_table(
    index=["userId"], columns=["title"], values="rating")

##############################################
# Adim 3 : Item-Based Film Onerilerinin Yapilmasi
##############################################

movie_name = "Matrix, The (1999)"

movie_name = user_movie_df[movie_name]

user_movie_df.corrwith(movie_name).sort_values(ascending=False)[1:11]


def check_film(keyword, user_movie_df):
    return [col for col in user_movie_df.columns if keyword in col]


check_film("Matrix", user_movie_df)
check_film("Sherlock", user_movie_df)


##############################################
# Adim 4 : Calisma Scriptinin Oluşturulması
##############################################

def create_user_movie_df():
    import pandas as pd
    movie = pd.read_csv('../movie_lens_dataset/movie.csv')
    rating = pd.read_csv('../movie_lens_dataset/ratings.csv')
    df = movie.merge(rating, how='left', on='movieId')
    comment_counts = pd.DataFrame(df["title"].value_counts())
    rare_movies = comment_counts[comment_counts["title"] <= 1000].index
    common_movies = df[~df["title"].isin(rare_movies)]
    user_movie_df = common_movies.pivot_table(
        index=["userId"], columns=["title"], values="rating")
    return user_movie_df


def item_based_recommender(movie_name, user_movie_df):
    movie_name = user_movie_df[movie_name]
    return user_movie_df.corrwith(movie_name).sort_values(ascending=False)[1:11]

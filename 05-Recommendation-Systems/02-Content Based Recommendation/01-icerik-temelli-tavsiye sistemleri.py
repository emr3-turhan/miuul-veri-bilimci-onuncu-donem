###########################################################
# PROJE 1: İÇERİK TEMELLİ TAVSİYE SİSTEMLERİ (CONTENT BASED RECOMMENDATION SYSTEMS)
###########################################################

########################
# İş Problemi
########################

# Yeni kurulmuş bir online film izleme platformu kullanıcılarına film önerilerinde bulunmak istiyor.

# Kullanıcılarının login oranı çok düşük olduğu için kullanıcı alışkanlıklarını toplayamamaktadır. Bu sebeple
# iş birlikçi filtreleme yöntemleri ile ürün önerileri geliştirememektedir.

# Fakat kullanıcılarının tarayıcıdaki izlerinden hangi filmleri izlediklerini bilmektedir. Bu bilgiye göre 
# film önerisinde bulununuz.


########################
# Veri Seti Hikayesi
########################

# movies_metadata.csv dosyası, 45.000'den fazla film hakkında bilgiler içermektedir. Bu veri seti, TMDB 5000
# Uygulama kapsamında film açıklamalarını içeren 'overview' değişkeni ile çalışılacaktır.

########################
# Film Overview'larına göre tavsiye sistemi geliştirme
########################

# 1. TF-IDF Matrisinin Oluşturulması
# 2. Cosine Similarity Matrisinin Oluşturulması
# 3. Benzerliklere Göre Önerilerin Yapılması
# 4. Çalışma Scriptinin Oluşturulması

########################
# 1. TF-IDF Matrisinin Oluşturulması
########################

import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option('display.expand_frame_repr', False)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_csv("../movies_metadata.csv", low_memory=False) # Dtype warning vermemesi için low_memory=False
df.head()

df["overview"].head()

tfidf = TfidfVectorizer(stop_words="english")

df[df["overview"].isnull()]

df["overview"] = df["overview"].fillna("")

tfidf_matrix = tfidf.fit_transform(df["overview"])

tfidf_matrix.shape

tfidf.get_feature_names()

tfidf_matrix.toarray()

########################
# 2. Cosine Similarity Matrisinin Oluşturulması
########################

cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)



########################
# 3. Benzerliklere Göre Önerilerin Yapılması
########################

indices = pd.Series(df.index, index=df["title"])

indices.index.value_counts() # Aynı film isminde birden fazla film var

indices = indices[~indices.index.duplicated(keep="last")] # Aynı film isminde birden fazla film varsa sonuncusunu al

indices["Cinderella"]

movie_index = indices["Sherlock Holmes"]

cosine_sim[movie_index]

similarity_scores = pd.DataFrame(cosine_sim[movie_index], columns=["score"])

movie_indices = similarity_scores.sort_values("score", ascending=False)[1:11].index

df["title"].iloc[movie_indices]


########################
# 4. Çalışma Scriptinin Oluşturulması
########################

def content_based_recommendation(title, cosine_sim, dataframe):
    # indeleri olusturma
    indices = pd.Series(dataframe.index, index=dataframe["title"])
    indices = indices[~indices.index.duplicated(keep="last")]
    # titleın indexini yakalama
    movie_index = indices[title]
    # title a gore benzerlik skorlarını olusturma
    similarity_scores = pd.DataFrame(cosine_sim[movie_index], columns=["score"])
    # kendisi haric ilk 10 filmi getirme
    movie_indices = similarity_scores.sort_values("score", ascending=False)[1:11].index
    return dataframe["title"].iloc[movie_indices]

def calculate_cosine_sim(dataframe):
    tfidf = TfidfVectorizer(stop_words="english")
    dataframe["overview"] = dataframe["overview"].fillna("")
    tfidf_matrix = tfidf.fit_transform(dataframe["overview"])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    return cosine_sim

cosine_sim = calculate_cosine_sim(df)
content_based_recommendation("Sherlock Holmes", cosine_sim, df)

# Veri tabani seviyesinde gerceklestirme. 100 200 film belirleyip onların verisini tutuyoruz.





























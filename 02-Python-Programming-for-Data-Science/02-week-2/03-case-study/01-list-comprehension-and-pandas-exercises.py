#######################################################################
# ## List Comprehensions ve Pandas Alistirmalar ##
# ## List Comprehensions and Pandas Exercises ##
# ## Listas de Comprensión y ejercicios de Pandas ##
#######################################################################

# > Gorev 1: List Comprehension yapisi kullanarak car_crashes verisindeki numerik degiskenlerin isimlerini buyuk harfe ceviriniz.
# > Task 1: Use the List Comprehension structure to convert the names of the numeric variables in the car_crashes data to uppercase.
# > Tarea 1: Utilice la estructura de comprensión de lista para convertir los nombres de las variables numéricas en mayúsculas.

import seaborn as sns # Veri setimizin icerisinde buludugu kutuphane / Library where our data set is located / Biblioteca donde se encuentra nuestro conjunto de datos
df = sns.load_dataset("car_crashes") # Veri setimizi df degiskenine atiyoruz / We assign our data set to the df variable / Asignamos nuestro conjunto de datos a la variable df
print(df.columns) # Veri setimizin sutunlarini yazdiriyoruz / We print the columns of our data set / Imprimimos las columnas de nuestro conjunto de datos

# -> Beklenen Cikti / Expected Output / Salida esperada:
# ["NUM_TOTAL","NUM_SPEEDING","NUM_ALCOHOL","NUM_NOT_DISTRACTED","NUM_NO_PREVIOUS","NUM_INS_PREMIUM","NUM_INS_LOSSES","ABBREV"]

# ==> Cozum / Solution / Solución:
num_cols   = [col for col in df.columns if str(df[col].dtypes) in ["float64","int64"]]
print(num_cols)



print([col.upper() + '_FLAG' if 'no' not in col else col.upper() for col in df.columns]
)
















# # DUZENLENECEK / TO BE EDITED / A EDITAR

# import pandas as pd
# import seaborn as sns

# # Görev 1: Seaborn kütüphanesi içerisinden Titanic veri setini tanımlayınız.
# df = sns.load_dataset("titanic")
# print(df.head())

# # Görev 2: Titanic veri setindeki kadın ve erkek yolcuların sayısını bulunuz.
# print(df["sex"].value_counts())

# # Görev 3: Her bir sutuna ait unique değerlerin sayısını bulunuz
# print(df.nunique())

# # Görev 4: pclass değişkeninin unique değerlerinin sayısını bulunuz.
# print(df["pclass"].nunique())

# # Görev 5: pclass ve parch değişkenlerinin unique değerlerinin sayısını bulunuz.
# print("**** pclass ****")
# print(df["pclass"].value_counts())
# print("**** parch ****")
# print(df["parch"].value_counts())

# # Görev 6: embarked değişkeninin tipini kontrol ediniz. Tipini category olarak değiştiriniz ve tekrar kontrol ediniz.
# print(df["embarked"].dtype)
# df["embarked"] = df["embarked"].astype("category")


# # Görev 7: embarked değeri C olanların tüm bilgelerini gösteriniz.
# print(df[df["embarked"] == "C"])

# # Görev 8: embarked değeri S olmayanların tüm bilgelerini gösteriniz.
# print(df[df["embarked"] != "S"])

# # Görev 9: Yaşı 30 dan küçük ve kadın olan yolcuların tüm bilgilerini gösteriniz.
# print(df[(df["age"] < 30) & (df["sex"] == "female")])

# # Görev 10: Fare'i 500'den büyük veya yaşı 70’den büyük yolcuların bilgilerini gösteriniz.
# print(df[(df["fare"] > 500) | (df["age"] > 70)])

# # Görev 11: Her bir değişkendeki boş değerlerin toplamını bulunuz.
# print(df.isnull().sum())

# # Görev 12: who değişkenini dataframe’den çıkarınız.
# print(df.drop("who", axis=1))

# # Görev 13: deck değikenindeki boş değerleri deck değişkenin en çok tekrar eden değeri (mode) ile doldurunuz.
# df['deck'].fillna(df['deck'].mode()[0], inplace=True)
# print(df["deck"].isnull().sum())
# print(df["deck"].head())

# # Görev 14: age değikenindeki boş değerleri age değişkenin medyanı ile doldurunuz
# df['age'].fillna(df['age'].median(), inplace=True)
# print(df["age"].isnull().sum())
# print(df["age"].head())

# # Görev 15: survived değişkeninin pclass ve cinsiyet değişkenleri kırılımınında sum, count, mean değerlerini bulunuz.
# print(df.groupby(["sex", "pclass"]).agg({"survived": ["sum", "count", "mean"]}))

# # Görev 16: 30 yaşın altında olanlar 1, 30'a eşit ve üstünde olanlara 0 verecek bir fonksiyon yazın. Yazdığınız fonksiyonu kullanarak titanik veri
# # setinde age_flag adında bir değişken oluşturunuz oluşturunuz. (apply ve lambda yapılarını kullanınız)
# df["age_flag"] = df.apply(lambda x: 1 if x["age"] < 30 else 0, axis=1)
# print(df.head())

# # Görev 17: Seaborn kütüphanesi içerisinden Tips veri setini tanımlayınız.
# df = sns.load_dataset("tips")
# print(df.head())

# # Görev 18: Time değişkeninin kategorilerine (Dinner, Lunch) göre total_bill değerinin sum, min, max ve mean değerlerini bulunuz
# print(df.groupby("time").agg({"total_bill": ["sum", "min", "max", "mean"]}))

# # Görev 19: Day ve time’a göre total_bill değerlerinin sum, min, max ve mean değerlerini bulunuz
# print(df.groupby(["day", "time"]).agg({"total_bill": ["sum", "min", "max", "mean"]}))

# # Görev 20: Lunch zamanına ve kadın müşterilere ait total_bill ve tip değerlerinin day'e göre sum, min, max ve mean değerlerini bulunuz.
# print(df[(df["time"] == "Lunch") & (df["sex"] == "Female")].groupby(["day"]).agg({"total_bill": ["sum", "min", "max", "mean"],"tip": ["sum", "min", "max", "mean"]}))

# # Görev 21: size'i 3'ten küçük, total_bill'i 10'dan büyük olan siparişlerin ortalaması nedir? (loc kullanınız)
# print(df.loc[(df["size"] < 3) & (df["total_bill"] > 10), "total_bill"].mean())

# # Görev 22: total_bill_tip_sum adında yeni bir değişken oluşturunuz. Her bir müşterinin ödediği totalbill ve tip in toplamını versin.
# df["total_bill_tip_sum"] = df["total_bill"] + df["tip"]
# print(df.head())
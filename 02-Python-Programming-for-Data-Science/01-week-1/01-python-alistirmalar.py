#######################################################################
# ## Python Alistirmalar ##
# ## Python Exercises ##
# ## Python Ejercicios ##
#######################################################################

# > Gorev 1: Verilen degerlerin veri yapilarini inceleyiniz.
# > Task 1: Analyze the data structures of the given values.
# > Tarea 1: Analice las estructuras de datos de los valores dados.

x = 8
y = 3.2
z = 8j + 18
a = "Hello World"
b = True
c = 23 < 22
l = [1, 2, 3, 4]
d = {"Name": "Jake", "Age": 27, "Adress": "Downtown"}
t = ("Machine Learning", "Data Science")
s = {"Python","MAchine Learning","Data Science"}

# - Type() metodunu kullaniniz.
# - Use the Type() method.
# - Utilice el método Type().

# ==> Cozum / Solution / Solución:

print(type(x))
# => 

print(type(y))
# =>

print(type(z))
# =>

print(type(a))
# =>

print(type(b))
# =>

print(type(c))
# =>

print(type(l))
# =>

print(type(d))
# =>

print(type(t))
# =>

print(type(s))
# =>

# > Gorev 2: Verilen string ifadenin tum harflerini buyuk harfe ceviriniz. Virgul ve nokta yerine space koyunuz, kelime kelime ayiriniz.
# > Task 2: Convert all letters of the given string to uppercase. Put a space instead of a comma and a period, separate the words.
# > Tarea 2: Convierta todas las letras de la cadena dada en mayúsculas. Ponga un espacio en lugar de una coma y un punto, separe las palabras.

text = "The goal is to turn data into information, and information into insight."

# -> Beklenen Cikti / Expected Output / Salida esperada:
# ['THE', 'GOAL', 'IS', 'TO', 'TURN', 'DATA', 'INTO', 'INFORMATION', 'AND', 'INFORMATION', 'INTO', 'INSIGHT']

# ==> Cozum / Solution / Solución:

text = text.replace(","," ") # Virgul yerine space koyduk. / We put a space instead of a comma. / Pusimos un espacio en lugar de una coma.
text = text.replace("."," ") # Nokta yerine space koyduk. / We put a space instead of a period. / Pusimos un espacio en lugar de un punto.
text = text.upper() # Tum harfleri buyuk harfe cevirdik. / We converted all letters to uppercase. / Convertimos todas las letras en mayúsculas.
text = text.split() # Kelime kelime ayirdik. / We separated the words. / Separamos las palabras.
print(text) # Ciktiyi yazdirdik. / We printed the output. / Imprimimos la salida.

# Istersek tum bu islemleri tek bir satirda da yapabiliriz.
# If we want, we can do all these operations in a single line. 
# Si queremos, podemos hacer todas estas operaciones en una sola línea.

text = "The goal is to turn data into information, and information into insight."
text = text.replace(","," ").replace("."," ").upper().split()
print(text)

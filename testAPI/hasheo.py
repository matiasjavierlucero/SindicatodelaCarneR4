import pymysql
import bcrypt



# db = pymysql.connect("64.225.47.18","mellitus","itecriocuarto2020","SindicatoCarneDB" )

# # prepare a cursor object using cursor() method
# cur = db.cursor()

# # execute SQL query using execute() method.

# cur.execute("SELECT id_usu , con_usu  FROM usuario")
# contrasenas = cur.fetchall()
# # print ('ids y contrasenas usuarios', contrasenas[0][1])
# usuycontra = []

# for usuario in contrasenas:
#     usuycontra.append ((usuario[0],usuario[1].encode('utf-8') ))
    
# print ('NO HASH')    
# print (usuycontra)

# usuycontrahash = []

# for idpass in usuycontra:
#     hashedpass = bcrypt.hashpw(idpass[1], bcrypt.gensalt(14))
#     usuycontrahash.append ((idpass[0],hashedpass))

# print ('HASHED')    
# print (usuycontrahash)

# for idypasshashed in usuycontrahash:
    
#     actualizarPasss = '''UPDATE usuario SET con_usu = %s WHERE id_usu = %s'''
#     values = (idypasshashed[1], idypasshashed[0],)
#     cur.execute (actualizarPasss,values)
#     db.commit()
    
    


#print(salt)
#print(hashed)



password = b"matias"
# Hash a password for the first time, with a randomly-generated salt
hashed = b'$2b$14$B16q9hmY0LKS2Th8u0bho.8CKN4OqJCf4MOlbDC8a4tProNInLSle'
# Check that an unhashed password matches one that has previously been
# hashed
if bcrypt.checkpw(password, hashed):
    print("It Matches!")
    print (password, '=>password')
    print ('hashed->', hashed)
else:
    print("It Does not Match :(")

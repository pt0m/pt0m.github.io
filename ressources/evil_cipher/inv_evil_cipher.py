"""
Code pour résoudre le challenge evil cipher proposé par la DGSE et ESIEE durant l'Opération Brigitte Friang

Author: Tom Pégeot

LSB a gauche dans les listes ! (indice 0)
"""
import numpy as np
from finitefield import *


#Operations dans GF(32)
#avec le polynome : X^5+ X^2 +1
GF32 = GF(2, [1,0,1,0,0])

def int_to_bin_list_5(a):
	v = [int(x) for x in "{:05b}".format(a)]
	return v[::-1]

def permutation15(a):
	b = []
	ordre = [7,3,13,8,12,10,2,5,0,14,11,9,1,4,6]
	for i in ordre:
		b.append(a[i])
	return b

def permutation(a):
	b        = [0 for i in range(45)]
	b[:15]   = permutation15(a[15:30])
	b[15:30] = permutation15(a[30:45])
	b[30:45] = permutation15(a[0:15])
	return b

def xor(l1, l2):
	l = []
	for i in range(len(l1)):
		l.append(1*(l1[i]^l2[i]))
	return l

#permet la conversion d'objet GF32 a nos liste de 0 et 1
def gf_to_list(gf):
	a = '{0:c}'.format(gf)
	l = [1*(x=='1') for x in a]
	while(len(l)<5): # normalement pas besoin mais pour etre sure
		print("Error: mauvaise taille de polynome n'est pas sensé arriver ! (la librairie devrait mettres les 0")
		l.append(0)
	return l

def galois_multiplication(a, b = [0,1,0,0,0]):
	gf_a = FiniteFieldElt(GF32,a)
	gf_b = FiniteFieldElt(GF32,b)
	gf_c = gf_a * gf_b
	#'{0:c}'.format(a)
	return gf_to_list(gf_c)

def galois_inverse(a):
	gf_a = FiniteFieldElt(GF32,a)
	gf_b = gf_a.inv()
	if(gf_b * gf_a != FiniteFieldElt(GF32, [1,0,0,0,0])):
		return gf_to_list(gf_a) #arrive quand on demande l'inverse de 0
	return gf_to_list(gf_b)

def round(d, key):
	tmp = [0 for i in range(45)]
	data = [0 for i in range(45)]
	tmp = permutation(d)
	#print("tmp" + "".join([str(x) for x in tmp]))
	for i in range(9):
		tmp[5*i: 5*i + 5] = galois_inverse(tmp[5*i:5*i+ 5])
	tmp = xor(tmp, key)
	for i in range(3):
		# 5 premiers bits
		data[15*i:15*i+5] = xor( xor( tmp[15*i:15*i+5], tmp[15*i+5:15*i+10]) , galois_multiplication(1*tmp[15*i+10:15*i+15]))
		# 5 suivants
		data[15*i+5:15*i+10] = xor( xor( tmp[15*i:15*i+5], galois_multiplication(1*tmp[15*i+5:15*i+10])) , tmp[15*i+10:15*i+15])
		# 5 suivants
		data[15*i+10:15*i+15] = xor( xor( galois_multiplication(1*tmp[15*i:15*i+5]), tmp[15*i+5:15*i+10]) , tmp[15*i+10:15*i+15])
	return data

def round_key(key):
	if(len(key)!=64):
		print("Error: taille de clef ne correspond pas dans al fonction round_key")
	key_tmp = 1*key
	#bidouillage mais les (1*) c'est pour avoir une copie profonde
	key_tmp[1:] = 1*key[:-1]
	key_tmp[0] = 1*key[63]
	#les xor a la con
	#key_tmp[9] = 1*key[63]
	key_tmp[9] = key[8]^key[63]
	key_tmp[34] = key[33]^key[63]
	key_tmp[61] = key[60]^key[63]
	return key_tmp

def key_expansion(key):
	reg = 1*key
	keys = []
	for i in range(6):
		#reg[8] = 0 #subtile a voir ! mais un resetn n'est pas connecté ! -- en fait c'est rien
		keys.append(1*reg[:45])
		reg = round_key(1*reg)
	return keys

def evil_cipher(key, din):
	reg_data = [0 for i in range(45)]
	ctr  = 0
	#load
	rkeys = key_expansion(key)
	reg_data = 1*din
	# rounds
	for ctr in range(6):
		if(ctr == 0):
			reg_data = xor(1*rkeys[ctr], 1*reg_data)
		else:
			reg_data = round(1*reg_data, 1*rkeys[ctr])
	return reg_data


# on initialise la clef
key = [int(x) for x in "{:064b}".format(0x4447534553494545)]
key = key[::-1]
#on met les 1 necessaire a gauche pour fair 64 bits
while len(key) < 64:
	print("key append 0")
	key.append(0)

#on prend le bloc à chiffré dans l'exemple
din = [int(x) for x in "011001010111011001101001011011000000000000000"]
din = din[::-1]
while len(din) < 45:
	print("din append 0")
	din.append(0)

#sortie attendu
dout = [int(x) for x in "000101110010110001110101010111010101001010100"]
dout = dout[::-1]


#on chiffre
sortie = evil_cipher(key, din)

if(sortie == dout): #on verifie que notre algorithme a fonctionné
	print("test chiffrement: ok !")




# ------------ INVERSE -------------------------------


def galois_div(a, div = [0,1,0,0,0]):
	gf_a = FiniteFieldElt(GF32,a)
	gf_b = FiniteFieldElt(GF32,div)
	gf_c = gf_a * gf_b.inv()
	#'{0:c}'.format(a)
	return gf_to_list(gf_c)

def permutation15_inv(b):
	a = []
	ordre = [8,12,6,1,13,7,14,0,3,11,5,10,4,2,9]
	for i in ordre:
		a.append(b[i])
	return a

def permutation_inv(b):
	a        = [0 for i in range(45)]
	a[15:30] = permutation15_inv(b[:15])
	a[30:45] = permutation15_inv(b[15:30])
	a[0:15] = permutation15_inv(b[30:45])
	return a

def round_inv(data, key):
	tmp = [0 for i in range(45)]
	for i in range(3):
		tmp[15*i: 15*i+5] =  galois_div( xor(galois_div(xor(data[15*i: 15*i+5], data[15*i + 5: 15*i+10]), div = [1,1,0,0,0]),data[15*i+10: 15*i+15]) , div =[0,1,0,0,0])
		tmp[15*i+5: 15*i+10] =  galois_div( xor(galois_div(xor(data[15*i: 15*i+5], data[15*i + 10: 15*i+15]), div = [1,1,0,0,0]),data[15*i+5: 15*i+10]) , div =[0,1,0,0,0])
		tmp[15*i+10: 15*i+15] =  galois_div( xor(galois_div(xor(data[15*i+5: 15*i+10], data[15*i + 10: 15*i+15]), div = [1,1,0,0,0]),data[15*i: 15*i+5]) , div =[0,1,0,0,0])
	tmp = xor(tmp, key)
	for i in range(9):
		tmp[5*i: 5*i +5] = galois_inverse(tmp[5*i:5*i+ 5])
	d = permutation_inv(tmp)
	return d


def evil_cipher_inv(key, dout):
	ctr = 0
	rkeys = key_expansion(key)
	reg_data = 1*dout
	for ctr in [5,4,3,2,1,0]:
		#print("".join([str(x) for x in reg_data]))
		if(ctr == 0):
			reg_data = xor(1*rkeys[ctr], 1*reg_data)
		else:
			reg_data = round_inv(1*reg_data, 1*rkeys[ctr])
	return reg_data




dechiffre = evil_cipher_inv(key, sortie)

if(dechiffre == din):
	print("test dechiffrement: ok !")


# ------------dechiffrement du vrai fichier --------------------------------

print("chargement du fichier a dechiffrer et parsing ...")

f = open("cipher.txt", "rb")
donnees_chiffrees = f.read()
f.close()
donnees_chiffrees = donnees_chiffrees.split(b"\n")


print("dechiffrement...")
# premiere partie (avant le '\n') , note : il n'y a peut etre pas besoin de séparer les parties avant et après le \n
blocks_1 = []
for i in range(len(donnees_chiffrees[0])//45):
	block = donnees_chiffrees[0][45*i: 45*(i+1)]
	block = block.decode('ascii')
	block = [int(i) for i in block]
	blocks_1.append(block)

blocks_1_dechiffree = []
for block in blocks_1:
	block_dechiffree = evil_cipher_inv(key, block[::-1])[::-1]
	block_dechiffree ="".join([str(i) for i in block_dechiffree])
	blocks_1_dechiffree.append(block_dechiffree)

# deuxieme partie (apres le '\n')
blocks_2 = []
for i in range(len(donnees_chiffrees[1])//45):
	block = donnees_chiffrees[1][45*i: 45*(i+1)]
	block = block.decode('ascii')
	block = [int(i) for i in block]
	blocks_2.append(block)

blocks_2_dechiffree = []
for block in blocks_2:
	block_dechiffree = evil_cipher_inv(key, block[::-1])[::-1]
	block_dechiffree ="".join([str(i) for i in block_dechiffree])
	blocks_2_dechiffree.append(block_dechiffree)

dechiffree = "".join(blocks_1_dechiffree) + "\n" + "".join(blocks_2_dechiffree)

print("ecriture du résultat dans dechiffree.txt")
f = open("dechiffree.txt", "w")
f.write(dechiffree)
f.close()

print("convertion ascii ...")

def bin_to_ascii_char(a):
	return chr(int(a,2))

def bin_to_ascii(bin_str):
	str_cp = 1*bin_str
	if(len(str_cp)%8 != 8):
		str_cp += "0"*(8-(len(str_cp)%8))
	result = ""
	for i in range(len(str_cp)//8):
		x = str_cp[i*8:(i+1)*8]
		result += bin_to_ascii_char(x)
	return result

dechiffree_ascii = bin_to_ascii("".join(blocks_1_dechiffree)) + "\n" + bin_to_ascii("".join(blocks_2_dechiffree))

print("ecriture du résultat dans dechiffree_ascii.txt")

f = open("dechiffree_ascii.txt", "w")
f.write(dechiffree_ascii)
f.close()

print(dechiffree_ascii)

"""
alpha = a + b + c'
beta  = a + b'+ c
gamma = a'+ b + c

"""

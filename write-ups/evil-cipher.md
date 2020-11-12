# Write-up "evil_cipher"”, hardware, Opération Brigitte Friang, DGSE, 2020

Voici mon write up pour "evil_cipher" un challenge proposé lors du ctf "Opération Brigitte Friang" par la DGSE et ESIEE.

C'est mon premier write-up, alors si il manque une explication n'hesitez pas à me prévenir à tom-pegeot@hotmail.fr

## Présentation du challenge
Tout d'abord le challenge viens avec l'énoncé suivant:
```
Evil Country a développé et implémenté sur FPGA son propre algorithme de chiffrement par blocs de 45 bits avec une clé de 64 bits. cipher.txt est un message chiffré avec la clé key=0x4447534553494545. Un agent a réussi à récupérer
- le code VHDL de l'algorithme (evil_cipher.vhd)
- la fin du package VHDL utilisé (extrait_galois_field.vhd)
- le schéma de la fonction permutation15 (permutation15.jpg)
- le schéma du composant key_expansion (key_expansion.jpg)

Un exemple de texte chiffré se trouve dans le fichier evil_example.txt (dans l'archive zip)

Déchiffrez le message.

Le flag est de la forme DGSESIEE{x} avec x un hash

evil_cipher.zip (SHA256=0b8ade55e61e2e0188cea2a3c004287ca16b9b1ee2951fa4ffe1b27963544434) : https://challengecybersec.fr/d3d2bf6b74ec26fdb57f76171c36c8fa/evil_cipher.zip
```
En somme il faut déchiffrer un fichier en aillant le code vhdl qui permet de systhetiser la puce de chiffrement.
Bonne nouvelle la clef est donnée !

## Exemple fournit

Alors c'est partit, on telecharge avec 'wget' pour ne pas utiliser la souris et faire plus pro. Dans l'archive fournit on trouve 6 fichiers.
![Alt Text](../ressources/evil_cipher/evil_cipher_ll1.png)

Puis on ouvre l'example:
![Alt Text](../ressources/evil_cipher/exemple.png)

On a donc un exemple qui chiffre code 45 bits avec la même clef donnée dans l'énoncé. (à noter que le code que le ficier à déchiffrer est égalemnt encodé avec des '0' et '1' ASCII)

Tout les autres fichier servent à décricre l'algorithme implémenté sur FPGA.

## Etude de l'algorithme

Tout d'abord on ouvre le evil-ciher

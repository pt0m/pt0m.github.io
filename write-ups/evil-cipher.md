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

<p align="center">
  <img src="../ressources/evil_cipher/evil_cipher_ll1.png">
</p>

Puis on ouvre l'exemple:
<p align="center">
  <img src="../ressources/evil_cipher/exemple.png">
</p>

On a donc un exemple qui chiffre code 45 bits avec la même clef donnée dans l'énoncé. (à noter que le code que le ficier à déchiffrer est égalemnt encodé avec des '0' et '1' ASCII)

Tout les autres fichier servent à décricre l'algorithme implémenté sur FPGA.

## Etude de l'algorithme

Tout d'abord on ouvre le fichier qui decrit la puce à la plus grande échelle. Ici après un rapide coup d'oeil on remarque qu'il s'agit de evil-ciher.vhd. (avoir déjà utilisé ou lut du vhdl peu aider ^^ )

<details>
<summary>Cliquer ici pour affichier le code de evil-cipher.vhd</summary>
<p>

```vhdl
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.galois_field.all;

--------------------------------------------
-- Operations dans GF(32)
-- avec le polynome : X^5+ X^2 +1
--------------------------------------------

entity evil_cipher is
  port (
    clk    : in  std_logic;
    resetn : in  std_logic;
    start  : in  std_logic;
    key    : in  std_logic_vector(63 downto 0);
    din    : in  std_logic_vector(44 downto 0);
    dout   : out std_logic_vector(44 downto 0);
    ready  : out std_logic
  );
end entity;

architecture rtl of evil_cipher is
  type state is (idle, cipher);
  signal current_state : state;
  signal next_state    : state;
  signal reg_data      : std_logic_vector(din'range);
  signal rkey          : std_logicc_vector(din'range);
  signal ctr           : natural range 0 to 5;
  signal load          : std_logic;
  signal busy          : std_logic;

begin
 ready <= not busy;
 dout <= (others => '0') when busy = '1'
         else reg_data;

 process(clk,resetn) is
 begin
   if resetn = '0' then
     current_state <= idle;     
     reg_data <= (others => '0');
     ctr      <= 0;

   elsif rising_edge(clk) then
     -- state register
     current_state <= next_state;

     -- counter
     if busy = '0' or ctr=5 then
       ctr <= 0;
     else
       ctr <= ctr+1;
     end if;

     -- data register
     if busy = '1' then
       if ctr = 0 then
         reg_data <= rkey xor reg_data;
       else
          reg_data <= round(reg_data,rkey);
       end if;
     elsif load = '1' then
       reg_data <= din;
     end if;
   end if;
 end process;

 exp : entity work.key_expansion
   port map (
     resetn => resetn,
     clk    => clk,
     load   => load,
     key    => key,
     rkey   => rkey
   );

   process (current_state, start, ctr) is
   begin
     case current_state is
       when idle =>
         if start = '1' then
           next_state <= cipher;  
         else
           next_state <= idle;  
         end if;
         busy <= '0';
         load <= start;
       when cipher =>
         if ctr < 5 then
           next_state <= cipher;  
         else
           next_state <= idle;  
         end if;
         busy <= '1';
         load <= '0';        
     end case;
   end process;


end architecture;
```
</p>
</details>

Tout d'abord on regarde les entrés de la puces qui sont decrites dans l'entité `evil_cipher`.

On y retrouve classiquement l'horloge `clk`, une entré pour `reset` la puce, une entrée `start` pour lancer le chiffrement, et `ready` qui doit probablement indiqué si la puce est prete ou bien si les données en sortie sont fixé (donc prete).
Mais les entrés qui nous interrese vraiment sont les 3 autres:
- `key` qui la clef qui est composé de 64 entré (1 ou 0). Donc la clef donnée est de la bonne taille (ouf!)
- `din` et `dout` qui sont composé de 45 bits (1 ou 0). Cela nous apprend que l'algorithme chiffre très certainement par bloc de 45 bits! ça tombe bien c'est exactemetn la taille des données chiffrées dans le fichier exemple.

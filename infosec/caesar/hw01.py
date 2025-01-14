message1 = "RANU CKKZ, UKQ WNA HAWNJEJC DKS PK QOA PDA YNULPWJWHUOEO KJ PDA OEILHA YWAOWN ODEBP YELDAN."
message2 = "MHILY LZA ZBHL XBPZXBL MVYABUHL HWWPBZ JSHBKPBZ JHLJBZ KPJABT HYJHUBT LZA ULBAYVU"
message3 = "WDL ADCV SXS IWXH WDBTLDGZ IPZT? WDETUJAAN XI LPH ATHH IWPC 20 BXCJITH."

ms = [message1, message2, message3]
import caesar

# repl_list = [('L','T'),('Z','H'),('A','E'),('Y','S'),('X','R')]
# modified = message2
# for r in repl_list:
#   modified = modified.replace(r[0], r[1])
# print(modified)

alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
alphabet_list = list(alphabet)

# hash = {}
# for m in message2:
#   if m in hash:
#     hash[m] += 1
#   else:
#     hash[m] = 1

# print(hash)
def minimum_scores(hashed):
  inverted_list = [(v,k) for k,v in hashed.items()]
  inverted_list.sort()
  return inverted_list

# print(minimum_scores(hash))
print(minimum_scores(caesar.score_all_keys(message2)))
print(caesar.brute_force(message2))
caesar.plot_frequencies(message2)

# def letter_score_frequencies(ciphertext, letter):
#   ''' takes ciphertext and given letter to replace. iterates through alphabet and returns scores for replaced letter'''
#   hashed = {}
#   modified_ciphertext = ciphertext
#   for c in alphabet:
#     modified_ciphertext = ciphertext.replace(letter, c)
#     hashed[c] = caesar.score_frequencies(caesar.calculate_frequencies(modified_ciphertext))
#   return hashed

# min_scores = minimum_scores(caesar.score_all_keys(message2))
# min_scores = caesar.calculate_frequencies(message2)

# modified = message2
# for i in range(len(min_scores)):
#   letter_freq = minimum_scores(letter_score_frequencies(modified, alphabet_list[i])) # finds smallest scores for a single letter change
#   modified.replace(alphabet_list[i], letter_freq[0][1]) # replaces that letter
# print(modified)
import pickle, os
translations_path = os.getenv("BOOKIE_PROCESSING")+'/nike/translations/' + 'hockey.pkl'
with open(translations_path, 'rb') as f:
    translations = pickle.load(f)

print(translations)
for key in translations.keys():
    if translations[key] == None:
        print(f'{key}:{translations[key]}')
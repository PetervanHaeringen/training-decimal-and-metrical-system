from flask import Flask, render_template, request, session
import random

app = Flask(__name__)
app.secret_key = 'een_geheime_sleutel'  # Vereist voor sessies

# Definieer eenheden
categorieen = ['lengte', 'oppervlakte', 'inhoud']
eenheden = {
    'lengte': ['km', 'hm', 'dam', 'm', 'dm', 'cm', 'mm'],
    'oppervlakte': ['km²', 'hm²', 'dam²', 'm²', 'dm²', 'cm²', 'mm²'],
    'inhoud': ['km³', 'hm³', 'dam³', 'm³', 'dm³', 'cm³', 'mm³']
}

# Conversiefactoren
conversie_factoren = {
    'lengte': {'km': 1e3, 'hm': 1e2, 'dam': 1e1, 'm': 1, 'dm': 1e-1, 'cm': 1e-2, 'mm': 1e-3},
    'oppervlakte': {'km²': 1e6, 'hm²': 1e4, 'dam²': 1e2, 'm²': 1, 'dm²': 1e-2, 'cm²': 1e-4, 'mm²': 1e-6},
    'inhoud': {'km³': 1e9, 'hm³': 1e6, 'dam³': 1e3, 'm³': 1, 'dm³': 1e-3, 'cm³': 1e-6, 'mm³': 1e-9}
}

# Positieve feedback
feedback_positief = ['Geweldig!', 'Fantastisch!', 'Super gedaan!', 'Je bent een rekenkampioen!', 'Top!']

def kies_eenheid(categorie):
    bron, doel = random.sample(eenheden[categorie], 2)
    return bron, doel

def omrekenen(categorie, bron, doel, waarde):
    waarde_in_basiseenheid = waarde * conversie_factoren[categorie][bron]
    return waarde_in_basiseenheid / conversie_factoren[categorie][doel]

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'punten' not in session:
        session['punten'] = 0
        session['categorie_index'] = 0
    
    huidige_categorie = categorieen[session['categorie_index']]
    
    if request.method == 'POST':
        bron, doel = request.form.get('bron_eenheid'), request.form.get('doel_eenheid')
        waarde, antwoord = float(request.form.get('waarde')), float(request.form.get('antwoord'))
        correct_antwoord = omrekenen(huidige_categorie, bron, doel, waarde)
        
        if abs(antwoord - correct_antwoord) < 1e-6:
            session['punten'] += 1
            resultaat = random.choice(feedback_positief)
        else:
            resultaat = f"Helaas, het juiste antwoord was {correct_antwoord:.12f}."
        
        if session['punten'] % 5 == 0 and session['punten'] > 0:
            if session['categorie_index'] < len(categorieen) - 1:
                session['categorie_index'] += 1
                resultaat += "<br>🎉 Je hebt een nieuwe categorie bereikt!"
            else:
                resultaat += "<br>🏆 Gefeliciteerd! Je hebt alles voltooid. Wil je opnieuw proberen?"
                session.clear()
    else:
        resultaat = None
    
    bron, doel = kies_eenheid(huidige_categorie)
    waarde = random.randint(1, 100)
    
    return render_template('index.html', resultaat=resultaat, bron_eenheid=bron, doel_eenheid=doel, waarde=waarde, eenheden=eenheden[huidige_categorie], punten=session['punten'], huidige_categorie=huidige_categorie)

if __name__ == '__main__':
    app.run(debug=True)


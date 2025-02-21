from flask import Flask, render_template, request, session
import random

app = Flask(__name__)
app.secret_key = 'een_geheime_sleutel'  # Vereist voor sessies

# Definieer eenheden voor lengte, oppervlakte en inhoud
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

# Feedback berichten
feedback_positief = [
    'Zo Slim!', 'Goed van je!', 'Briljant!', 'Jij bent gewoon heel goed!', 
    'Verbluffend!', 'Geniaal!', 'Nog even en je bent EindBaasMetriek!'
]

def kies_eenheid(categorie):
    bron, doel = random.sample(eenheden[categorie], 2)  # Zorgt dat ze niet hetzelfde zijn
    return bron, doel

def omrekenen(categorie, bron_eenheid, doel_eenheid, waarde):
    waarde_in_basiseenheid = float(waarde) * conversie_factoren[categorie][bron_eenheid]
    return waarde_in_basiseenheid / conversie_factoren[categorie][doel_eenheid]

def geef_feedback():
    return random.choice(feedback_positief)

@app.route('/', methods=['GET', 'POST'])
def index():
    # Reset teller bij herstart
    if 'reset' not in session:
        session['punten'] = 0
        session['categorie_index'] = 0
        session['reset'] = True

    categorien = ['lengte', 'oppervlakte', 'inhoud']
    huidige_categorie = categorien[session['categorie_index']]

    if request.method == 'POST':
        try:
            bron_eenheid = request.form.get('bron_eenheid')
            doel_eenheid = request.form.get('doel_eenheid')
            waarde = float(request.form.get('waarde'))  # Zorgt dat waarde een float is
            antwoord = float(request.form.get('antwoord'))  # Converteer input naar float

            correct_antwoord = omrekenen(huidige_categorie, bron_eenheid, doel_eenheid, waarde)

            if abs(antwoord - correct_antwoord) < 1e-6:
                session['punten'] += 1
                resultaat = geef_feedback()
            else:
                resultaat = f"Helaas, het juiste antwoord was {correct_antwoord:.12f}."

            # Ga naar de volgende categorie na 5 goede antwoorden
            if session['punten'] % 5 == 0 and session['punten'] > 0:
                session['categorie_index'] = (session['categorie_index'] + 1) % len(categorien)
                huidige_categorie = categorien[session['categorie_index']]  # Vernieuw de categorie
                bron_eenheid, doel_eenheid = kies_eenheid(huidige_categorie)  # Kies nieuwe eenheden
                waarde = random.randint(1, 100)  # Kies nieuwe waarde

            # Controleer of alle categorieën zijn voltooid
            if session['categorie_index'] == 0 and session['punten'] >= len(categorien) * 5:
                resultaat = "Gefeliciteerd! Je hebt alle categorieën voltooid!"

        except ValueError:
            resultaat = "Ongeldige invoer, probeer opnieuw."

    else:
        resultaat = None

    # Genereer nieuwe oefening
    bron_eenheid, doel_eenheid = kies_eenheid(huidige_categorie)
    waarde = random.randint(1, 100)

    return render_template(
        'index.html', 
        resultaat=resultaat, 
        bron_eenheid=bron_eenheid, 
        doel_eenheid=doel_eenheid, 
        waarde=waarde, 
        eenheden=eenheden[huidige_categorie], 
        punten=session['punten'], 
        huidige_categorie=huidige_categorie
    )


if __name__ == '__main__':
    app.run(debug=True)

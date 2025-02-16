from flask import Flask, render_template, request, session
import random

app = Flask(__name__)
app.secret_key = 'geheime_sleutel'  # Nodig voor sessiebeheer

# Definieer eenheden voor lengte, oppervlakte en inhoud
eenheden = {
    'lengte': ['km','hm','dam', 'm', 'dm','cm', 'mm'],
    'oppervlakte': ['km²','hm²','dam²', 'm²', 'dm²','cm²', 'mm²'],
    'inhoud': ['km³','hm³','dam³', 'm³', 'dm³','cm³', 'mm³']
}


# mogelijke feedback
feedback_positief = ['Zo Slim!','Goed van je!','Briljant!','Jij bent gewoon heel goed!','Verbluffend!','Geniaal!','Goed! maar Pas Op zo wordt je een Nerd!','Je lijkt wel een wandelende Rekenmachine!']

# Correcte conversiefactoren
conversie_factoren = {
    'lengte': {'km': 1e3, 'hm': 1e2, 'dam': 1e1, 'm': 1, 'dm': 1e-1, 'cm': 1e-2, 'mm': 1e-3
    },
    'oppervlakte': {
        'km²': 1e6, 'hm²': 1e4, 'dam²': 1e2, 'm²': 1, 'dm²': 1e-2, 'cm²': 1e-4, 'mm²': 1e-6
    },
    'inhoud': {
        'km³': 1e9, 'hm³': 1e6, 'dam³':1e3, 'm³': 1, 'dm³':1e-3, 'cm³': 1e-6, 'mm³': 1e-9
    }
}

categorie_volgorde = ['lengte', 'oppervlakte', 'inhoud']


def kies_eenheid(categorie):
    return random.choice(eenheden[categorie])

def omrekenen(categorie, bron_eenheid, doel_eenheid, waarde):
    waarde_in_basiseenheid = waarde * conversie_factoren[categorie][bron_eenheid]
    waarde_in_doel_eenheid = waarde_in_basiseenheid / conversie_factoren[categorie][doel_eenheid]
    return waarde_in_doel_eenheid

def geef_feedback(categorie_volgorde):
    return random.choice(categorie_volgorde)

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'scores' not in session or 'reset' in request.form:
        session['scores'] = {'lengte': 0, 'oppervlakte': 0, 'inhoud': 0}
        session['huidige_categorie'] = 'lengte'
        session.pop('oefening', None)
    
    huidige_categorie = session['huidige_categorie']
    scores = session['scores']
    resultaat = None
    oefening = session.get('oefening')
    
    if scores['inhoud'] >= 10:
        return render_template('index.html', resultaat="Gefeliciteerd! Je bent geslaagd!", eenheden=eenheden)
    
    if 'start' in request.form or oefening is None:
        while True:
            bron_eenheid = kies_eenheid(huidige_categorie)
            doel_eenheid = kies_eenheid(huidige_categorie)
            if bron_eenheid != doel_eenheid:
                break
        waarde = random.randint(1, 100)
        oefening = {'bron_eenheid': bron_eenheid, 'doel_eenheid': doel_eenheid, 'waarde': waarde}
        session['oefening'] = oefening
    
    elif 'controleer' in request.form:
        try:
            bron_eenheid = oefening['bron_eenheid']
            doel_eenheid = oefening['doel_eenheid']
            waarde = oefening['waarde']
            antwoord = float(request.form.get('antwoord'))
            
            correct_antwoord = omrekenen(huidige_categorie, bron_eenheid, doel_eenheid, waarde)
            
            if round(antwoord, 6) == round(correct_antwoord, 6):
                resultaat = geef_feedback(feedback_positief)
                scores[huidige_categorie] += 1
                session['oefening'] = None  # Reset oefening voor een nieuwe opgave
            else:
                resultaat = f"Helaas, het juiste antwoord was {correct_antwoord:.6f}."
            
            session['scores'] = scores
            
            if scores[huidige_categorie] >= 10:
                huidige_index = categorie_volgorde.index(huidige_categorie)
                if huidige_index < len(categorie_volgorde) - 1:
                    session['huidige_categorie'] = categorie_volgorde[huidige_index + 1]
                    session.pop('oefening', None)
                else:
                    return render_template('index.html', resultaat="Gefeliciteerd! Je bent geslaagd!", eenheden=eenheden)
        except (ValueError, TypeError):
            resultaat = "Ongeldige invoer. Zorg ervoor dat je een geldig getal invoert."
    
    return render_template('index.html', resultaat=resultaat, categorie=huidige_categorie, 
                           bron_eenheid=oefening['bron_eenheid'], doel_eenheid=oefening['doel_eenheid'], waarde=oefening['waarde'], eenheden=eenheden, scores=scores)

if __name__ == '__main__':
    app.run(debug=True, port=8080)

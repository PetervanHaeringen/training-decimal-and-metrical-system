from flask import Flask, render_template, request, session
import random

app = Flask(__name__)
app.secret_key = 'een_geheime_sleutel'  # Vereist voor het gebruik van sessies

# Definieer eenheden voor decimaal stelsel en metrieke stelsel
eenheden = {
    'decimal': ['powers of 10', 'shifting decimal', 'scientific notation'],
    'metric': ['lengte', 'oppervlakte', 'inhoud']
}

# Conversiefactoren voor decimaal stelsel en metrieke stelsel
conversie_factoren = {
    'decimal': {'powers of 10': 1, 'shifting decimal': 1, 'scientific notation': 1},
    'metric': {
        'lengte': {'km': 1e3, 'hm': 1e2, 'dam': 1e1, 'm': 1, 'dm': 1e-1, 'cm': 1e-2, 'mm': 1e-3},
        'oppervlakte': {'km²': 1e6, 'hm²': 1e4, 'dam²': 1e2, 'm²': 1, 'dm²': 1e-2, 'cm²': 1e-4, 'mm²': 1e-6},
        'inhoud': {'km³': 1e9, 'hm³': 1e6, 'dam³': 1e3, 'm³': 1, 'dm³': 1e-3, 'cm³': 1e-6, 'mm³': 1e-9}
    }
}

# Mogelijke feedback
feedback_positief = [
    'Zo Slim!', 'Goed van je!', 'Briljant!', 'Jij bent gewoon heel goed!', 
    'Verbluffend!', 'Geniaal!', 'Goed! maar Pas Op zo wordt je een Nerd!', 
    'Je lijkt wel een wandelende Rekenmachine!'
]

def geef_feedback():
    return random.choice(feedback_positief)

def generate_powers_of_10_exercise():
    power = random.randint(-4, 4)  # Willekeurige macht tussen -4 en 4
    coefficient = random.randint(1, 9)  # Willekeurige coefficient tussen 1 en 9
    question = f"What is {coefficient} × 10^{power}?"
    correct_answer = coefficient * (10 ** power)
    return question, correct_answer

def generate_shifting_decimal_exercise():
    number = round(random.uniform(1, 100), 2)  # Willekeurig getal met 2 decimalen
    power = random.randint(-3, 3)  # Willekeurige macht tussen -3 en 3
    question = f"What is {number} × 10^{power}?"
    correct_answer = number * (10 ** power)
    return question, correct_answer

def generate_scientific_notation_exercise():
    number = round(random.uniform(0.001, 1000), 4)  # Willekeurig getal tussen 0.001 en 1000
    question = f"Write {number} in scientific notation."
    # Bereken wetenschappelijke notatie
    a, b = f"{number:e}".split('e')
    correct_answer = f"{float(a):.4f} × 10^{int(b)}"
    return question, correct_answer

def kies_eenheid(categorie):
    eenheden_lijst = eenheden[categorie]
    bron_eenheid = random.choice(eenheden_lijst)
    doel_eenheid = random.choice(eenheden_lijst)
    
    # Zorg ervoor dat bron_eenheid en doel_eenheid niet hetzelfde zijn
    while bron_eenheid == doel_eenheid:
        doel_eenheid = random.choice(eenheden_lijst)
    
    return bron_eenheid, doel_eenheid

def omrekenen(categorie, bron_eenheid, doel_eenheid, waarde):
    # Converteer naar de basiseenheid (bijv. meter, vierkante meter, kubieke meter)
    waarde_in_basiseenheid = waarde * conversie_factoren[categorie][bron_eenheid]
    # Converteer naar de doel eenheid
    waarde_in_doel_eenheid = waarde_in_basiseenheid / conversie_factoren[categorie][doel_eenheid]
    return waarde_in_doel_eenheid

@app.route('/', methods=['GET', 'POST'])
def index():
    # Initialiseer sessievariabelen als ze nog niet bestaan
    if 'punten' not in session:
        session['punten'] = 0
    if 'categorie_index' not in session:
        session['categorie_index'] = 0

    categorien = ['decimal', 'metric']
    huidige_categorie = categorien[session['categorie_index']]

    if request.method == 'POST':
        if huidige_categorie == 'decimal':
            exercise_type = request.form.get('exercise_type')
            if exercise_type == 'powers of 10':
                question = request.form.get('question')
                correct_answer = float(request.form.get('correct_answer'))
            elif exercise_type == 'shifting decimal':
                question = request.form.get('question')
                correct_answer = float(request.form.get('correct_answer'))
            elif exercise_type == 'scientific notation':
                question = request.form.get('question')
                correct_answer = request.form.get('correct_answer')
            
            antwoord = request.form.get('antwoord')
            if antwoord == str(correct_answer):
                session['punten'] += 1
                resultaat = geef_feedback()
            else:
                resultaat = f"Helaas, het juiste antwoord was {correct_answer}."
        else:
            bron_eenheid = request.form.get('bron_eenheid')
            doel_eenheid = request.form.get('doel_eenheid')
            waarde = float(request.form.get('waarde'))
            antwoord = float(request.form.get('antwoord'))
            
            correct_antwoord = omrekenen(huidige_categorie, bron_eenheid, doel_eenheid, waarde)
            if abs(antwoord - correct_antwoord) < 1e-6:
                session['punten'] += 1
                resultaat = geef_feedback()
            else:
                resultaat = f"Helaas, het juiste antwoord was {correct_antwoord:.12f}."

        # Ga naar de volgende categorie na 5 goede antwoorden
        if session['punten'] % 5 == 0 and session['punten'] > 0:
            session['categorie_index'] = (session['categorie_index'] + 1) % len(categorien)
    else:
        resultaat = None

    # Genereer een nieuwe oefening
    if huidige_categorie == 'decimal':
        exercise_type = random.choice(['powers of 10', 'shifting decimal', 'scientific notation'])
        if exercise_type == 'powers of 10':
            question, correct_answer = generate_powers_of_10_exercise()
        elif exercise_type == 'shifting decimal':
            question, correct_answer = generate_shifting_decimal_exercise()
        elif exercise_type == 'scientific notation':
            question, correct_answer = generate_scientific_notation_exercise()
        
        return render_template('index.html', resultaat=resultaat, question=question, correct_answer=correct_answer, exercise_type=exercise_type, eenheden=eenheden[huidige_categorie], punten=session['punten'], huidige_categorie=huidige_categorie)
    else:
        bron_eenheid, doel_eenheid = kies_eenheid(huidige_categorie)
        waarde = random.randint(1, 100)
        return render_template('index.html', resultaat=resultaat, bron_eenheid=bron_eenheid, doel_eenheid=doel_eenheid, waarde=waarde, eenheden=eenheden[huidige_categorie], punten=session['punten'], huidige_categorie=huidige_categorie)

if __name__ == '__main__':
    app.run(debug=True)
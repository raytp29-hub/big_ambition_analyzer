import pandas as pd 
import re 
import io



# utils/cleaner.py
import pandas as pd
import re
import io

def pulisci_csv_big_ambitions(uploaded_file):
    
    try:
        # Leggi il contenuto del file
        stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
        lines = stringio.readlines()
        
        righe_sistemate = []
        
        for riga in lines:
            # Applica regex per trovare pattern
            match = re.match(r'^(.*?)(,"?\d+"?,.*)$', riga.strip())
            if match:
                descrizione = match.group(1)
                resto = match.group(2)
                
                # Aggiungi virgolette se mancanti
                if not descrizione.startswith('"'):
                    riga = f'"{descrizione}"{resto}\n'
            
            # Converti virgole in punto e virgola
            dentro_virgolette = False
            nuova_riga = ""
            
            # Da controllare sicuramente esiste un metodo migliore e più performante
            for carattere in riga:
                if carattere == '"':
                    dentro_virgolette = not dentro_virgolette
                    nuova_riga += carattere
                elif carattere == ',' and not dentro_virgolette:
                    nuova_riga += ";"
                else:
                    nuova_riga += carattere
            
            righe_sistemate.append(nuova_riga)
        
        # Crea stringa pulita con header
        csv_pulito = '"description";"day";"type";"price";"balance"\n'
        csv_pulito += ''.join(righe_sistemate)
        
        # Converti in DataFrame
        df = pd.read_csv(io.StringIO(csv_pulito), delimiter=';')
        
        return df, None
        
    except Exception as e:
        return None, f"Errore nella pulizia: {str(e)}"
    
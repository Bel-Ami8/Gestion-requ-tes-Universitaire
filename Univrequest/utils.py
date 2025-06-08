from io import BytesIO
from django.core.files.base import ContentFile
from django.template.loader import get_template
from django.utils import timezone
from xhtml2pdf import pisa

from Univrequest.models import Requetes

def generer_pdf_rapport(date_debut, date_fin, utilisateur, periode):
    # Récupérer les requêtes dans la période
    requetes = Requetes.objects.filter(date_creation__range=(date_debut, date_fin))

    # Statistiques
    total_requetes = requetes.count()
    types_requete_freq = {}
    for req in requetes:
        types_requete_freq[req.type_requete] = types_requete_freq.get(req.type_requete, 0) + 1

    type_requete_courant = max(types_requete_freq, key=types_requete_freq.get) if types_requete_freq else "N/A"

    # Délai moyen de traitement (en jours)
    delai_moyen = 0
    delais = []
    for req in requetes:
        if hasattr(req, 'date_traitement') and req.date_traitement:
            delta = (req.date_traitement - req.date_creation).days
            delais.append(delta)

    if delais:
        delai_moyen = round(sum(delais) / len(delais), 2)

    # Contexte pour le template
    context = {
    'date_debut': date_debut,
    'date_fin': date_fin,
    'periode': periode,
    'requetes': requetes,
    'total_requetes': total_requetes,
    'type_requete_courant': type_requete_courant,
    'delai_moyen': delai_moyen,
    'receptionniste': utilisateur.get_full_name() or utilisateur.username,
    'now': timezone.now(),
    'types_requete_freq': types_requete_freq,  # ✅ Ajout
    'filiere': utilisateur.filiere if hasattr(utilisateur, 'filiere') else None,  # ✅ Ajout
     }
    # Génération du PDF
    template = get_template("rapport_pdf_template.html")
    html = template.render(context)
    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)

    if pisa_status.err:
        return None, None

    nom_pdf = f"rapport_{periode}_{timezone.now().strftime('%Y%m%d%H%M%S')}.pdf"
    fichier_content = ContentFile(result.getvalue())
    return nom_pdf, fichier_content

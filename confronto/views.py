from django.shortcuts import redirect, render

from hub.auth import app_login_required, current_username

from .caricamento import ErroreFile
from .esecuzione import esegui_giro
from .forms import ModuloGiro
from .risultati import CATEGORIE, leggi_ultimo_giro


@app_login_required
def risultati(request):
    """Pagina principale: risultati dell'ultimo giro. Se non ce n'e', al modulo."""
    dati = leggi_ultimo_giro()
    if dati is None:
        return redirect("confronto:nuovo")
    return render(request, "confronto/risultati.html", {"d": dati, "categorie": CATEGORIE})


@app_login_required
def nuovo(request):
    """
    Modulo per un nuovo confronto.
    Dopo un giro riuscito si torna alla pagina dei risultati con un redirect
    (schema Post/Redirect/Get): premendo F5 il browser non reinvia i file.
    """
    errore = None
    if request.method == "POST":
        modulo = ModuloGiro(request.POST, request.FILES)
        if modulo.is_valid():
            f = modulo.cleaned_data
            try:
                esegui_giro(
                    current_username(request),
                    {k: f[k] for k in ("sku_alias", "sku_old", "batch_notes")},
                    {k: f[k] for k in ("batch", "sales_order", "package", "giacenza")},
                )
                return redirect("confronto:risultati")
            except ErroreFile as e:
                errore = str(e)
    else:
        modulo = ModuloGiro()

    return render(request, "confronto/nuovo.html", {"modulo": modulo, "errore": errore})

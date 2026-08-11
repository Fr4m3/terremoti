# Terremoti Italia — pagina GitHub Pages

Pagina statica con i **terremoti recenti rilevati dalla Rete Sismica
Nazionale (INGV)**, in tempo reale. Stesso schema di [meteo-pisa](https://github.com/Fr4m3/meteo-pisa).

- `index.html` — pagina statica: carica i dati **live dall'API INGV**
  direttamente nel browser (CORS permesso); se la rete è giù usa
  `terremoti.json` come fallback
- `terremoti.json` — istantanea dello snapshot (rigenerata ogni giorno da cron sul telefono)
- `fetch_terremoti.py` — scarica gli ultimi eventi dal servizio FDSNWS INGV
  e scrive `terremoti.json`
- `aggiorna_ghpages.sh` — rigenera lo snapshot e pubblica su GitHub Pages
  (da schedulare con cron, vedi sotto)

## Crontab (sul telefono, Termux)

```
0 6 * * * ~/terremoti/aggiorna_ghpages.sh >> ~/terremoti/logs/aggiorna.log 2>&1
```

URL: <https://fr4m3.github.io/terremoti/>

Dati: INGV — <https://terremoti.ingv.it> / <https://webservices.ingv.it>
## Aggiornamento automatico

La pagina è servita da GitHub Pages e lo snapshot `terremoti.json` viene rigenerato automaticamente dal workflow GitHub Actions ogni 3 ore (oltre all'esecuzione manuale dal tab Actions). Ogni evento include **distanza e direzione (azimut) da casa** — Viale delle Cascine 124, Pisa (43.7247258 N, 10.3802555 E).

## Rischio di sequenza

Dal pannello **⚡ Rischio di sequenza** (cliccando `🔬` su una riga della tabella, il link nel popup della
mappa o la card dell'evento più forte) la pagina stima, **partendo da un singolo evento**, la probabilità
che segua una sequenza sismica — cioè una o più repliche. Il calcolo avviene nel browser, in tempo reale,
sul catalogo INGV degli ultimi 30 giorni attorno all'epicentro (raggio adattivo in base alla magnitudo):

- **Legge di Omori modificata** (p=1): il numero atteso di repliche cresce come `K·ln((t+c)/c)` con `c=0.01` gg; `K` è stimato dalle repliche già osservate,
- **Gutenberg-Richter**: il parametro `b` è stimato con MLE (Utsu) sul catalogo locale ≥ completezza `Mc` (adattiva: 1.0 → 0.5),
- **Legge di Båth**: massima replica attesa ≈ M dell'evento − 1.2 (±0.5),
- **Processo di Poisson**: probabilità di almeno 1 scossa ≥ M in 24 h / 72 h / 7 gg / 30 gg / 90 gg = `1 − exp(−λ)`.

Il pannello mostra una **gauge con la percentuale** (soglia e finestra selezionabili: ≥ M2.0…3.5 × 24 h…90 gg),
la tabella delle probabilità per tutte le soglie, le repliche totali attese (ML ≥ 1.0) e il livello di rischio
(Basso / Moderato / Elevato / Molto elevato). Valori preliminari: non sono previsioni deterministiche.

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

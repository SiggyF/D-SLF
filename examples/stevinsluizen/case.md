| Kolom | Eenheid | Definitie |
| :--- | :--- | :--- |
| `time` | s | Tijd vanaf het begin van de simulatie waarop de betreffende ZSF-routine start. Routine 1/3 gebruikt Start Leveling; routine 2/4 gebruikt Start Doors Opening. |
| `head_sea` | m | Waterstandsverschil tussen zeezijde en meerzijde: Water level side 1 − Water level side 2. Side 1 is de zeezijde. |
| `routine` | – | Fase van de lockcyclus: 1 = leveling zee → meer, 2 = openen meerzijde, 3 = leveling meer → zee, 4 = openen zeezijde. |
| `salinity_lake` | – | Saliniteitsniveau aan de meerzijde. In de huidige conversie leeg gelaten. |
| `salinity_sea` | – | Saliniteitsniveau aan de zeezijde. In de huidige conversie leeg gelaten. |
| `ship_volume_lake_to_sea` | m³ | Volume waterverplaatsing door schepen die meer → zee gaan. Wordt bij Routine 2 ingevuld op basis van de volgende Side 2-lockage. |
| `ship_volume_sea_to_lake` | m³ | Volume waterverplaatsing door schepen die zee → meer gaan. Wordt bij Routine 4 ingevuld op basis van de volgende Side 1-lockage. |
| `t_flushing` | s | Duur van een eventuele flushing-/spoelfase. In de huidige conversie leeg gelaten. |
| `t_level` | s | Duur van het nivelleren van de kolk. Overgenomen uit Leveling duration (min) en omgerekend naar seconden. Alleen bij Routine 1 en 3. |
| `t_open_lake` | s | Effectieve open-periode aan de meerzijde. Berekend vanaf het midden van Start Doors Opening–Start Sailing Out van de huidige lockage tot het midden van Start Doors Closing–Start Leveling van de volgende lockage. |
| `t_open_sea` | s | Effectieve open-periode aan de zeezijde. Zelfde berekening als t_open_lake, maar voor de zeedoorstroming. |
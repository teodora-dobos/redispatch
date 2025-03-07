# Interactive Redispatch Data Dashboard

This repository includes a Python streamlit dashboard app which visualizes the redispatch data for Germany, 2024, obtained from [Netztransparenz](https://www.netztransparenz.de/de-de/Systemdienstleistungen/Betriebsfuehrung/Redispatch). 

Since the original dataset does not include the geographic coordinates of the redispatched units, their location is identified first.

## Key Features
- Geographic localization of redispatched units using fuzzy matching
- Data visualization based on unit type and redispatch direction
- Daily statistics indicating the total redispatch volume, the number of redispatched units and the number of redispatch measures


## Data Sources
The data used in this project was obtained from the following open sources:
- [Netztransparenz:](https://www.netztransparenz.de/de-de/Systemdienstleistungen/Betriebsfuehrung/Redispatch) 
    - redispatch data for the time interval 31.12.2023 - 31.12.2024
- [Open Power System Data:](https://data.open-power-system-data.org/conventional_power_plants/ 
) 
    - list of conventional power plants from Germany
      
## Screenshot
![image](redispatch/image.png)

## Usage
```bash
pip install -r requirements.txt
streamlit run app.py  
```

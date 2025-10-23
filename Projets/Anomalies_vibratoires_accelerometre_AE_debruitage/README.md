# Détection d'anomalies vibratoires avec capteur accéléromètre et auto-encodeur de débruitage
[![Article lié](https://img.shields.io/badge/Article_lié-000?logo=Medium)](https://medium.com/@antoninlefevre45/auto-encodeur-de-débruitage-pour-la-détection-danomalies-vibratoires-117d2ad3a94b) &nbsp; [![PyTorch](https://img.shields.io/badge/PyTorch-FFF?logo=pytorch)]() &nbsp;  [![Arduino](https://img.shields.io/badge/Arduino-FFF?logo=Arduino)]() &nbsp; [![Streamlit](https://img.shields.io/badge/Streamlit-FFF?logo=streamlit)]()

Ce projet permet de détecter les chocs en temps réel à l'aide d'un modèle d'autoencodeur de débruitage et d'un capteur d'accélération. 
L'objectif est d'identifier les chocs parmi les données du capteur en éliminant le bruit et les variations normales d'accélération.
Nous utiliserons le capteur MPU-6050 (GY-521) et un Arduino Uno pour collecter les données d'accélération. L'interface pour visualiser 
les données en temps réel est développé avec Streamlit. 

Pour lancer l'interface, exécutez la commande suivante dans le dossier du projet :

```bash
streamlit run streamlit_real_time_interface.py
```
 
<br>

<p align="center">
  <img src="preview.png" alt="preview projet anoamlies detection" width="800">
</p>

<br>
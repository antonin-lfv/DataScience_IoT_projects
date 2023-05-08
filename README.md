
<h1 align="center">
  <br>
  <a href="http://www.amitmerchant.com/electron-markdownify"><img src="images/background.png" alt="Markdownify" width="700"></a>
  <br><br>
  Data science & IoT
  <br>
</h1>

<h4 align="center">Découvrez la data science sur Arduino et Raspberry Pi au travers de divers projets.</h4>

<p align="center">
 <a href="#"><img src="https://img.shields.io/badge/Raspberry_Pi-FFF?logo=raspberry+pi&logoColor=C51A4A" alt="Raspberry Pi"></a>
 &nbsp;
 <a href="#"><img src="https://img.shields.io/badge/Arduino-FFF?logo=arduino" alt="Arduino"></a>
 &nbsp;
 <a href="#"><img src="https://img.shields.io/badge/PyTorch-FFF?logo=pytorch" alt="PyTorch"></a>
 &nbsp;
 <a href="#"><img src="https://img.shields.io/badge/Scikit--learn-FFF?logo=scikitlearn" alt="Scikit-learn"></a>
&nbsp;
 <a href="#"><img src="https://img.shields.io/badge/Streamlit-FFF?logo=streamlit" alt="Streamlit"></a>

</p>

<p align="center">
  <a href="#liens-utiles">Liens utiles</a> •
  <a href="#introduction">Introduction</a> •
  <a href="#projets">Projets</a>
</p>

<br>

# Liens utiles

- Documentation [Arduino](https://docs.arduino.cc/?_gl=1*q1xbuk*_ga*MTE1NjQ3NzM5Mi4xNjI5OTk4MDM0*_ga_NEXN8H46L5*MTYzMTIyMDEzMy4xMi4xLjE2MzEyMjAxMzMuMA..)

- Chaîne YouTube [U=RI](https://www.youtube.com/channel/UCVqx3vXNghSqUcVg2nmegYA) <br>

- Chaîne YouTube [BoilingBrains](https://www.youtube.com/channel/UCKAzZCVzqkdvxX6VLTwyVMQ) <br>

<br>

# Introduction

Dans ce dépôt, vous trouverez une collection de projets combinant **IoT** et **Data Science**, en utilisant les plateformes **Arduino** et **Raspberry Pi**. Les codes sources sont disponibles et accompagnés d'instructions détaillées pour faciliter leur reproduction. En intégrant l'Internet des objets et l'intelligence artificielle, ces projets visent à explorer les applications pratiques et les limites de ces technologies dans divers domaines. N'hésitez pas à suggérer de nouveaux projets à inclure et à partager vos impressions sur ceux déjà présents.

Pour faciliter la recherche en fonction de vos besoins, chaque projet est doté de badges. Les **badges noirs** sont des liens servant à rediriger vers le code source ou un article lié. Les **badges blancs** correspondent aux outils utilisés pour le projet, comme le framework de data science ou le matériel utilisé. 

<br>

# Projets

### Détection d'anomalies vibratoires avec capteur accéléromètre et auto-encodeur de débruitage
[![Code source](https://img.shields.io/badge/Code_source-000?logo=Visual+Studio+Code)](Projets/Anomalies_vibratoires_accelerometre_AE_debruitage/streamlit_real_time_interface.py) &nbsp; [![Article lié](https://img.shields.io/badge/Article_lié-000?logo=Medium)](https://medium.com/@antoninlefevre45/auto-encodeur-de-débruitage-pour-la-détection-danomalies-vibratoires-117d2ad3a94b) &nbsp; [![PyTorch](https://img.shields.io/badge/PyTorch-FFF?logo=pytorch)]() &nbsp;  [![Arduino](https://img.shields.io/badge/Arduino-FFF?logo=Arduino)]() &nbsp; [![Streamlit](https://img.shields.io/badge/Streamlit-FFF?logo=streamlit)]()

Ce projet permet de détecter les chocs en temps réel à l'aide d'un modèle d'autoencodeur de débruitage et d'un capteur d'accélération. 
L'objectif est d'identifier les chocs parmi les données du capteur en éliminant le bruit et les variations normales d'accélération.
Nous utiliserons le capteur MPU-6050 (GY-521) et un Arduino Uno pour collecter les données d'accélération. L'interface pour visualiser 
les données en temps réel est développé avec Streamlit. 

Pour lancer l'interface, exécutez la commande suivante dans le dossier du projet :

```bash
streamlit run streamlit_real_time_interface.py
```

<p align="center">
  <br>
  <img src="Projets/Station_meteo_prediction_temps_ML/preview.jpg" alt="preview projet anoamlies detection" width="1200">
  <br>
</p>


<br>

---

> Website [antoninlefevre.com](https://antonin-lfv.github.io) &nbsp;&middot;&nbsp;
> GitHub [@antonin-lfv](https://github.com/antonin-lfv) &nbsp;&middot;&nbsp;
> Linkedin [@antonin](https://www.linkedin.com/in/antonin-lefevre-0110)


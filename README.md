# lk-ihc-vera
Imported from code.google.com/p/lkihc-vera-integration

Integrates Lauritz Knudsens (LK) Intelligent House Concept (IHC) with Micasaverde Vera Z-Wave Home Automation Controller

As LK IHC is mostly marked in Denmark, most of the documentation will be in danish

# LK IHC Vera Integration

This project integrates Lauritz Knudsen IHC (Intelligent House Concept) with Micasaverde Vera (Z-Wave gateway)

As LK IHC is mainly marked and used in Denmark, most of these pages will be in danish

## Introduction

Setupet består af 3 dele:

## Vera Plugin
En plugin skrevet i Lua, der opsætter devices matchende IHC installationen. Kommunikere med Gateway programmet via sockets

Dette findes i vera/IHC folderen

Bemærk: Er kun testet på en Vera 3 med UI5!

## Gateway program
Et python program, der kommunikere med Vera'en via en socket (som socket server) og IHC Controlleren via SOAP (benytter SUDS).

IHC Controlleren skal formentlig være med Viewer (kun testet mod denne)

Dette program findes i ihcclient folderen

## IHC funktionsblokke
Disse er ikke længere nødvendig

## Installation
Konfigurer Gateway programmet (config.py) og start det på "gateway deviced" - Kun testet på en Synology NAS, men kan helt sikkert bringes til  at køre på meget andet

Installere Vera plugin'et: Upload filerne, opret et device med I_IHC.xml
Opsæt ip og port på dette device så det peger på Gateway programmet
Sæt AutoCreate til 1: Så vil der blive oprettet child devises:
  * BinaryLigth1: For hver udgangsport på IHC samt Wireless relæ
  * DimmanbleLigth1: For Wireless dimmere
  * SceneController: For 4-tryk: Svagstrømstryk, Kombirelæere og dimmere.
Disse kan udføre Scene number 1 til 4 for de 4 tryk:

```
    1 2
    3 4
```

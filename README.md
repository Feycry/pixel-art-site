# pixel-art-site
A pixel art sharing website

## Sovelluksen tämänhetkinen tila

* Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
* Käyttäjä pystyy lisäämään png kuvia.
* Käyttäjä näkee sovellukseen lisätyt teokset.
* Käyttäjä pystyy kommentoimaan toisten käyttäjien teoksista.
* Käyttäjä pystyy muokkaamaan ja poistamaan omia kommenttejaan.
* Käyttäjä pystyy etsimään teoksia tagilla.
* Sovelluksessa on käyttäjäsivut, jotka näyttävät tilastoja ja käyttäjän lisäämät teokset sekä kommentit.

## Sovelluksen tavoitteet

* ~~Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.~~
* Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan 32x32 pikselitaideteoksia.
* ~~Käyttäjä pystyy lisäämään teoksille tageja.~~
* ~~Käyttäjä näkee sovellukseen lisätyt teokset.~~
* ~~Käyttäjä pystyy etsimään teoksia tagilla.~~
* ~~Sovelluksessa on käyttäjäsivut, jotka näyttävät tilastoja ja käyttäjän lisäämät teokset sekä kommentit.~~
* ~~Käyttäjä pystyy kommentoimaan toisten käyttäjien teoksista.~~

## Lisätavoitteita, jotka eivät välttämättä toteudu

* Sisään rakennettu editori, jolla käyttäjä voi luoda teoksia (tulee olemaan haaste ilman javascriptiä).
* Etukäteen määriteltyjä väripaletteja, joista käyttäjän tulee valita (teoksia voidaan täten tallentaa pienempään kokoon).
* Kyky katsella lisättyjä teoksia eri paleteilla, kuin millä ne on julkaistu.
* Kyky lisätä myös 16x16 ja 64x64 teoksia.
* Käyttäjä pystyy tykkäämään toisten käyttäjien teoksista.
* Sovellus näyttää hyvältä (CSS)

## Sovelluksen asennus

Asenna `flask`-kirjasto:

```
$ pip install flask
```

Luo tietokanta:

```
$ sqlite3 database.db < schema.sql
```

Voit käynnistää sovelluksen näin:

```
$ flask run
```
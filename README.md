## Dots and Boxes

## Cerinte
- [x] Setup-ul jocului
    - [x] Selectare algoritm (IDA*, Alpha-Beta sau retele bayesiene)
    - [x] Selectare dificultate
    - [x] Selectare simbol jucator
- [x] Afisari
    - [x] Input gresit (mesaj eroare)
    - [x] Afisare jucator curent
    - [x] Afisare noua stare a jocului
    - [x] Afisare rezultat + punctaj + timp de joc 
- [x] Generarea succesorilor. Testarea validitatii mutarilor
- [x] Testarea starii finale. Stabilirea castigatorului. Calcularea scorului
- [x] 2 moduri diferite de estimare a scorului pentru stari intermediare
- [x] Stabilirea urmatoarei mutari conform algoritmului IDA*  
- [x] Stabilirea urmatoarei mutari conform algoritmului Alpha-Beta  
- [ ] Stabilirea urmatoarei mutari folosind retele Bayesiene
- [x] Claritatea codului
    - [x] Variabile cu nume intuitive
    - [x] Codul va fi impartit in functii cu nume intuitiv de maxim o pagina fiecare
    - [x] Se va trata cazul in care functiile sunt apelate cu parametrii invalizi 
- [x] Comentarii
    - [x] Explicarea pe scurt a fiecarei functii
    - [x] Explicarea algoritmului de generare a mutarilor
    - [x] Explicarea estimarii scorului
    - [x] Explicatia euristicii alese pentru MAX
- [x] Interfata grafica


## Adancimi obtine cu timp de raspuns rezonabil
|  Size  | (n, 2) | (n, 3) | (n, 4) | (n, 5) | (n, 6) | (n, 7) |
| ------ | ------ | ------ | ------ | ------ | ------ | ------ |
| (2, m) |    -   |   7    |   10   |   7    |   6    |   6    |
| (3, m) |    7   |   7    |   6    |   5    |   5    |   4    |
| (4, m) |   10   |   6    |   5    |   5    |   4    |   4    |
| (5, m) |    7   |   5    |   5    |   4    |   4    |   3    |
| (6, m) |    6   |   5    |   4    |   4    |   3    |   3    |
| (7, m) |    6   |   4    |   4    |   3    |   3    |   2    |


## Build
```bash
cd scripts
exe_build.bat
```

sau

```bash
pyinstaller main.spec
```

## Run
#### Python (no exe)
```bash
cd scripts
run.bat
```

#### Exe (build required)
```bash
cd scripts
exe_run.bat
```

sau

```bash
cd dist
Dots_and_Boxes.exe
```

## Resurse
- [Heart Model](https://github.com/liuyubobobo/heart-curve-cplusplus)
- [Colorama](https://pypi.org/project/colorama/)
- [PyGame](https://www.pygame.org/docs/)
- [PyInstaller](https://www.pyinstaller.org/)
- [PyTest](https://docs.pytest.org/en/latest/)
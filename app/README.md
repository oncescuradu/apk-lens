# APK Lens — Windows 11 x64

Aplicație desktop locală pentru codul Java reconstruit din APK și liniile adăugate/modificate între două versiuni. Nu trimite APK-urile pe servere.

## Pornire

1. Instalează Python 3.12+ x64 de la https://www.python.org/downloads/windows/ cu Tkinter și Python Launcher.
2. Instalează Java 17+ x64 și descarcă distribuția JADX de la https://github.com/skylot/jadx/releases (neinclusă în acest proiect).
3. Dezarhivează proiectul și deschide `start.bat`.
4. Apasă **Alege JADX** și selectează `bin/jadx.bat` din distribuția JADX.
5. Importă APK-ul vechi, apoi APK-ul nou, în ordinea versiunilor. Selectează veche → nouă și apasă **Compară**.
6. Filtrează după cale sau cod, sortează după fișier/linie ori numărul adăugirilor, selectează o linie și vezi contextul evidențiat verde. Exportul CSV include rezultatele afișate.

Versiunile sunt păstrate în `%LOCALAPPDATA%\APK Lens\project`. Importurile persistă între porniri. Pentru altă aplicație, mută acest folder înainte de pornire. Compară doar versiuni ale aceleiași aplicații.

## Executabil

Rulează `build.bat` pe Windows 11 x64 cu Python x64. Executabilul apare în `dist\APK-Lens.exe`; Java și JADX rămân dependențe externe. Construirea și interfața Windows necesită verificare pe Windows; proiectul nu include un executabil deja construit.

## Ce înseamnă „recent”

Diferențele sunt relative la perechea de versiuni selectată. Ordinea importurilor reprezintă ordinea versiunilor, nu data reală de scriere a codului. O înlocuire este afișată ca linie nouă. Nu există o dată individuală pentru fiecare linie în APK. Codul obfuscat poate genera diferențe fără schimbări funcționale; folosește aceeași versiune JADX pentru toate importurile.

Java este reconstruit, nu sursa originală: comentariile, numele originale și codul eliminat nu sunt recuperabile. Codul de pe server și bibliotecile native `.so` nu sunt decompilate de această versiune. Nu include încă vizualizare Smali sau decodare Apktool. Resursele text produse de JADX se văd dezactivând filtrul Java/Kotlin. Erorile JADX sunt păstrate în `jadx.log` împreună cu rezultatele parțiale, fără înregistrarea versiunii incomplete.

## Verificare

`python -m unittest discover -s tests -v`

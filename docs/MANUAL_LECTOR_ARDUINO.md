# Manual: detectar el formato de una tarjeta con el lector Arduino

Esta función sirve para descubrir **qué formato Wiegand usa una tarjeta** cuando
solo conoces el número **impreso** en ella. El Arduino captura los bits que manda
el lector, la app busca qué parte de esos bits corresponde al número impreso y te
propone el formato listo para cargar en el reloj IN01.

---

## 1. Qué necesitas

> Si el PC aún no tiene Python, Git ni el IDE de Arduino, sigue antes
> [INSTALACION.md](INSTALACION.md).

| Elemento | Detalle |
|---|---|
| Arduino | Uno, Nano o Mega (5 V). Con ESP32 hace falta un conversor de nivel. |
| Lector de tarjetas Wiegand | Idealmente **el mismo modelo que va conectado al reloj**. |
| Fuente para el lector | La que pida el lector (normalmente 12 V). |
| Cable USB | Del Arduino al PC. |
| PC con la app | Python 3 y la carpeta `formatos-wiegand-custom` actualizada (`git pull`). |
| Navegador | **Chrome o Edge** (Firefox no permite usar el puerto serie). |
| 2–3 tarjetas | Distintas entre sí, con su número impreso visible. |

---

## 2. Conexión del lector al Arduino

| Cable del lector | Va a |
|---|---|
| Rojo (+V) | Positivo de la fuente del lector |
| Negro (GND) | Negativo de la fuente **y** GND del Arduino (masa común, obligatorio) |
| Verde (D0) | Pin **2** del Arduino |
| Blanco (D1) | Pin **3** del Arduino |

> Si el lector no tiene la masa unida a la del Arduino, no llegan lecturas o
> llegan con bits al azar.

---

## 3. Cargar el programa en el Arduino (solo la primera vez)

1. Abre el **IDE de Arduino**.
2. Abre `arduino/wiegand_lector/wiegand_lector.ino` de la carpeta del proyecto.
3. Elige la placa y el puerto COM (*Herramientas → Placa / Puerto*).
4. Pulsa **Subir**.
5. (Opcional) Abre el *Monitor Serie* a **115200** y pasa una tarjeta. Debe salir
   una línea como:

   ```
   WG 26 11001000000010111111101001 HEX=3202FE9
   # como W26: site=144 card=6132 paridad=OK
   ```

6. **Cierra el Monitor Serie** antes de seguir: si queda abierto, la app no puede
   usar el puerto.

---

## 4. Abrir la app

En una terminal, dentro de la carpeta del proyecto:

```
cd "C:\Users\Marcelo Fuentes\Downloads\formatos-wiegand-custom"
git pull
python app.py --port 8080 --myip 192.168.2.103
```

Abre en Chrome o Edge **`http://127.0.0.1:8080/`**.

> Importante: usa `127.0.0.1`, **no** la IP de red (`192.168.x.x`). El navegador
> solo deja usar el puerto serie desde `127.0.0.1`.

---

## 5. Leer tarjetas y buscar el formato

La sección está arriba de todo: **«Lector Arduino — detectar formato de la tarjeta»**.

1. Pulsa **Conectar Arduino** y elige el puerto COM del Arduino. El indicador pasa
   a *Conectado · esperando tarjeta*.
2. **Pasa una tarjeta** por el lector. Aparece en *Lecturas* con su largo
   (`26 bits`, `35 bits`, …) y los bits.
3. En el cuadro de la derecha escribe el **número impreso** de esa tarjeta:
   - solo el número de tarjeta: `6132`
   - o site y tarjeta separados por coma: `144,6132`
4. Repite con **2 o 3 tarjetas distintas**.
5. Pulsa **Buscar formato** (o Enter en el cuadro del número).

Sin Arduino a mano también puedes escribir la lectura en *agregar a mano* (los
bits `0/1` o la línea `WG …` completa) junto con su número impreso, y pulsar
**Agregar lectura**.

---

## 6. Cómo leer el resultado

Cada candidato muestra:

- **Nombre**: si coincide con un formato conocido sale su nombre (`Wiegand26`,
  `HIDCorp35`, …); si no, `LectorNN`.
- **Etiqueta verde «cuadra con todas»**: el formato explica todas las lecturas y
  la paridad da bien en todas. **Es el que buscas.**
- **Etiqueta amarilla «parcial»**: falla en alguna lectura; descártalo.
- **Card_Format coloreado**: `E`/`O` paridad, `S` site, `C` número de tarjeta.
- Por cada lectura: `✓ impreso 6132 → site 144 · card 6132 · paridad OK`.
- **Avisos ⚠** a tener en cuenta (por ejemplo, «con una sola tarjeta la paridad
  puede cuadrar por azar»).

El primero de la lista es el más probable. **Fíate solo si dice «cuadra con
todas» con 2 o más tarjetas**; con una sola, la paridad puede coincidir por
casualidad.

### Ejemplos reales

| Lectura | Resultado | Formato a usar |
|---|---|---|
| 26 bits, impreso `6132` | site 144 · card 6132 | **Wiegand26a** (`ESSSSSSSSCCCCCCCCCCCCCCCCO`) |
| 35 bits, impreso `8958` | company 3787 · card 8958 | **HIDCorp35** (HID Corporate 1000) |

---

## 7. Pasar el formato al reloj

1. En el candidato correcto pulsa **Usar en el editor**.
2. En el editor revisa:
   - **Nombre**: ponle un nombre claro (máx. 24 caracteres). Para las de 26 bits con
     site separado usa `Wiegand26a`, que es el nombre de fábrica.
   - **Tipo**: `entrada / lectura (tipo 3)`.
   - **Status**: `1 — activo`.
3. (Opcional) **★ Guardar como preconfigurado** para no tener que leer tarjetas la
   próxima vez.
4. **Agregar a la tabla ▾**.
5. En *Tabla a cargar*: modo **«Reescribir tabla (fábrica + mis formatos)»**,
   archivo `u.sql`, y **Generar update.sql**. El mensaje debe decir
   *«la carga fijará ExtWGInBitsCount=NN…»* con el largo de tu formato.
6. En *Cargar en el reloj IN01*: elige el **SN**, pulsa **Ver comandos exactos**
   (debe aparecer la línea `SET OPTIONS ExtWGInBitsCount=NN,…`) y luego
   **Cargar en el reloj (reinicia)**.
7. Cuando el reloj reinicie, pasa una tarjeta: debe marcar el **número impreso**.

---

## 8. Problemas frecuentes

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| El botón dice que el navegador no permite Web Serial | Firefox, o abriste la app por la IP de red | Chrome/Edge en `http://127.0.0.1:8080/` |
| No se puede abrir el puerto | Monitor Serie del IDE abierto | Ciérralo y vuelve a conectar |
| Conectado pero no aparecen lecturas | Falta masa común, D0/D1 cruzados o lector sin alimentación | Revisa la conexión (sección 2) |
| «ningún tramo de bits coincide con el número impreso» | Número mal escrito, o el impreso no está en los bits (algunas tarjetas imprimen otro dato) | Revisa el número; prueba solo la parte de tarjeta; lee otra tarjeta |
| Varios candidatos «cuadra con todas» | Pocas lecturas | Lee más tarjetas distintas |
| El reloj muestra un número **distinto** al impreso | El formato activo toma otros bits (p. ej. `Wiegand26` de fábrica junta site y card: 144·65536+6132 = 9443572) | Carga el formato detectado (p. ej. `Wiegand26a`) |
| Con formato de 26, una tarjeta de 35 da un número raro (p. ej. 22545) | El reloj corta la trama de 35 y usa los **primeros** 26 bits | Usa el formato de 35 bits detectado |
| El formato se ve en el menú pero **no lee** | Largo distinto al de las tarjetas, o el firmware no acepta ese esquema de paridad | Verifica el largo (26/35) con el Arduino; ver la nota sobre HIDCorp35 |

### Nota sobre HID Corporate 1000 (35 bits)

Tiene 3 bits de paridad que se verifican entre sí. Ningún formato de fábrica del
IN01 hace eso, así que el firmware podría no aceptarlo. Para comprobarlo, con
HIDCorp35 cargado, envía desde el panel (`/panel`, comandos libres):

```
SET OPTIONS ExtHaveParityBits=0
REBOOT
```

Si así lee el número impreso, el formato es correcto y solo falla la paridad.
Para volver a dejarlo como estaba: `SET OPTIONS ExtHaveParityBits=1` y `REBOOT`.
Con la paridad desactivada el reloj acepta cualquier trama de ese largo
(incluidas lecturas con ruido).

### Recordatorio: un formato de entrada a la vez

El IN01 tiene **un solo formato de entrada activo**. Si activas uno de 35 bits,
las tarjetas de 26 dejan de leer en ese reloj, y al revés.

# Instalación desde cero (Windows)

Todo lo necesario para dejar funcionando la app de formatos Wiegand en un PC
nuevo: Python, Git, el proyecto, el IDE de Arduino y la conexión con el reloj
IN01. Los comandos se escriben en **PowerShell** (botón Inicio → escribir
`PowerShell` → Enter).

> La app **no necesita instalar librerías extra**: usa solo lo que trae Python.

---

## Resumen rápido

Para quien ya conoce los pasos (detalle de cada uno más abajo):

```powershell
winget install -e --id Python.Python.3.13
winget install -e --id Git.Git
winget install -e --id ArduinoSA.IDE.stable
# cerrar y volver a abrir PowerShell
cd $HOME\Downloads
git clone https://github.com/Marcelo-Fuentes/formatos-wiegand-custom.git
cd formatos-wiegand-custom
python app.py --port 8080 --myip <IP_DE_ESTE_PC>
```

---

## 1. Instalar Python 3

**Opción A (recomendada), con winget:**

```powershell
winget install -e --id Python.Python.3.13
```

**Opción B, con el instalador:**

1. Descarga Python 3 desde https://www.python.org/downloads/windows/
2. Al abrir el instalador, **marca la casilla «Add python.exe to PATH»** (abajo).
3. Pulsa *Install Now*.

**Comprobar** (cierra y vuelve a abrir PowerShell primero):

```powershell
python --version
```

Debe responder algo como `Python 3.13.x`. Si en cambio se abre la Microsoft
Store o dice que no se reconoce el comando:

- Prueba `py --version`. Si funciona, usa `py` en lugar de `python` en todos los
  comandos de esta guía.
- O desactiva el alias de la tienda: *Configuración → Aplicaciones → Configuración
  avanzada de aplicaciones → Alias de ejecución de aplicaciones →* apagar
  `python.exe` y `python3.exe`.

---

## 2. Instalar Git

Sirve para bajar el proyecto y actualizarlo con un solo comando (`git pull`).

```powershell
winget install -e --id Git.Git
```

(o el instalador de https://git-scm.com/download/win con las opciones por defecto)

Comprobar (en una PowerShell nueva):

```powershell
git --version
```

> **Sin Git:** en https://github.com/Marcelo-Fuentes/formatos-wiegand-custom
> pulsa *Code → Download ZIP* y descomprímelo. Funciona igual, pero para
> actualizar tendrás que volver a descargar el ZIP.

---

## 3. Descargar el proyecto

```powershell
cd $HOME\Downloads
git clone https://github.com/Marcelo-Fuentes/formatos-wiegand-custom.git
cd formatos-wiegand-custom
```

Queda en `C:\Users\<tu usuario>\Downloads\formatos-wiegand-custom`.

**Actualizar** a la última versión (cada vez que haya cambios):

```powershell
cd $HOME\Downloads\formatos-wiegand-custom
git pull
```

Si el repositorio se clonó con la dirección antigua (`Taric-kun/...`), corrígela
una vez:

```powershell
git remote set-url origin https://github.com/Marcelo-Fuentes/formatos-wiegand-custom.git
```

**Comprobar que todo está bien** (opcional):

```powershell
python tests/test_core.py
python tests/test_loader_backup.py
python tests/test_detect.py
```

Cada uno debe terminar con `... passed, 0 failed`.

---

## 4. Saber la IP del PC

El reloj tiene que poder llegar a este PC por la red.

```powershell
ipconfig
```

Busca el adaptador con el que estás conectado (Wi-Fi o Ethernet) y anota la
**Dirección IPv4** (ej. `192.168.2.103`). No uses `127.0.0.1` ni la de una VPN.

---

## 5. Iniciar la app

```powershell
cd $HOME\Downloads\formatos-wiegand-custom
python app.py --port 8080 --myip 192.168.2.103
```

(cambia `192.168.2.103` por tu IP del paso 4)

Debe mostrar:

```
App Wiegand en  http://192.168.2.103:8080/   (panel crudo en /panel)
Apunta el reloj: SET OPTIONS WebServerURLModel=0,WebServerPort=8080,ICLOCKSVRURL=192.168.2.103,IsSupportSSL=0   y luego REBOOT
```

- **Deja esa ventana abierta**: si la cierras, la app se detiene.
- Para detenerla: `Ctrl + C` en esa ventana.
- Si dice que el puerto está en uso, mira qué lo ocupa y ciérralo:

  ```powershell
  netstat -ano | findstr :8080
  taskkill /PID <número_de_la_última_columna> /F
  ```

  o usa otro puerto (`--port 8090`), recordando cambiarlo también en el reloj.

**Abrir la app:** en Chrome o Edge, `http://127.0.0.1:8080/`.
El panel crudo de comandos está en `http://127.0.0.1:8080/panel`.

| Parámetro | Para qué | Por defecto |
|---|---|---|
| `--port` | Puerto en el que escucha (debe ser el mismo `WebServerPort` del reloj) | `8080` |
| `--myip` | IP del PC que se usa en las URLs de descarga para el reloj | se detecta sola |
| `--host` | Interfaz donde escucha | `0.0.0.0` (todas) |
| `--capdir` | Carpeta donde se guardan los archivos que manda el reloj | `captures` |

---

## 6. Firewall de Windows

Si el reloj no aparece en la app, lo más común es que Windows bloquee la conexión.
La primera vez que inicias la app Windows puede preguntar si permitir Python:
marca **redes privadas** (y públicas si tu red figura como pública) y acepta.

Si no preguntó, crea la regla a mano (PowerShell **como administrador**):

```powershell
netsh advfirewall firewall add rule name="ZK Push 8080" dir=in action=allow protocol=TCP localport=8080
```

Comprobar que la app está escuchando:

```powershell
netstat -ano | findstr :8080
```

Debe aparecer una línea con `0.0.0.0:8080 ... LISTENING`.

---

## 7. Apuntar el reloj IN01 a este PC

El reloj debe enviar sus datos a la app. Configúralo con estos valores (desde el
menú *Comunicación → Nube/ADMS*, o con el comando que muestra la app al iniciar):

| Opción | Valor |
|---|---|
| Servidor (`ICLOCKSVRURL`) | IP del PC (paso 4) |
| Puerto (`WebServerPort`) | El mismo `--port` de la app (8080) |
| `WebServerURLModel` | `0` (por IP) |
| HTTPS / `IsSupportSSL` | `0` (desactivado) |

Después **reinicia el reloj**. En 1–2 minutos aparece en la app (chip verde
«1 reloj · <SN>») y en el log del panel sale `NUEVO EQUIPO SN=...`.

Si no aparece: verifica IP y puerto exactos, que el reloj esté en la misma red
(prueba `ping <IP_del_reloj>`), el firewall (paso 6) y que el reloj se haya
reiniciado después de cambiar la configuración.

---

## 8. Arduino (solo para detectar formatos de tarjeta)

1. Instala el IDE de Arduino:

   ```powershell
   winget install -e --id ArduinoSA.IDE.stable
   ```

   (o desde https://www.arduino.cc/en/software)

2. Conecta el Arduino por USB. Si Windows no lo reconoce (clones con chip
   CH340), instala el driver CH340 del fabricante del chip.
3. Abre `arduino\wiegand_lector\wiegand_lector.ino` de la carpeta del proyecto,
   elige *Placa* y *Puerto* en el menú *Herramientas* y pulsa **Subir**.
4. Conexión del lector y uso: ver [MANUAL_LECTOR_ARDUINO.md](MANUAL_LECTOR_ARDUINO.md).

Para usar el Arduino desde la app hace falta **Chrome o Edge** abriendo
`http://127.0.0.1:8080/` (no la IP de red).

---

## 9. Comandos útiles del día a día

| Qué | Comando |
|---|---|
| Ir a la carpeta | `cd $HOME\Downloads\formatos-wiegand-custom` |
| Actualizar el proyecto | `git pull` |
| Iniciar la app | `python app.py --port 8080 --myip <IP>` |
| Detener la app | `Ctrl + C` en su ventana |
| Ver la IP del PC | `ipconfig` |
| Ver si el puerto está en uso | `netstat -ano \| findstr :8080` |
| Cerrar un proceso que ocupa el puerto | `taskkill /PID <PID> /F` |
| Probar que el reloj responde | `ping <IP_del_reloj>` |
| Correr las pruebas | `python tests/test_core.py` (y los demás de `tests\`) |

### Comandos para el reloj (panel `/panel` → comandos libres)

| Qué | Comando |
|---|---|
| Apuntar el reloj a la app | `SET OPTIONS WebServerURLModel=0,WebServerPort=8080,ICLOCKSVRURL=<IP>,IsSupportSSL=0` |
| Reiniciar el reloj | `REBOOT` |
| Largo del lector de entrada (bits) | `SET OPTIONS ExtWGInBitsCount=26` |
| Desactivar / activar verificación de paridad del lector | `SET OPTIONS ExtHaveParityBits=0` / `=1` |
| Ver los archivos de datos | `shell ls -la /mnt/mtdblock/data/` |
| Traer una copia de la base | usar *Traer copia de ZKDB.db* en la app |

Las opciones `SET OPTIONS` se aplican después de `REBOOT`.

---

## 10. Siguiente paso

- Detectar el formato de una tarjeta: [MANUAL_LECTOR_ARDUINO.md](MANUAL_LECTOR_ARDUINO.md)
- Visión general de la app y sus reglas: [README](../README.md)

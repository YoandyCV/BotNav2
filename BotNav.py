# This Python file uses the following encoding: utf-8
from config import *
import imapclient, imaplib, pyzmail, smtplib, time, os, re
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.audio import  MIMEAudio
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders
from os.path import basename

import requests, queue, threading, openai, pyzipper, random
from bs4 import BeautifulSoup
import urllib.parse
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO

from conexion import live
import subprocess
import py7zr
from pytube import YouTube
from pytube.exceptions import VideoUnavailable
from queue import Queue
import shutil



# Ampliando la limitación imap
imaplib._MAXLINE = 1000000
global cliente
global i
global s

# Crea una lista para almacenar los mensajes
conversation = []

# Crear una cola para almacenar las URLs
cola_youtube = Queue()
cola_youtube2 = Queue()
cola_descarga = Queue()


# Variable de control para verificar si el sub proceso está en ejecución
subproceso_youtube = None
subproceso_youtube2 = None
subproceso_descarga = None




#-----------MODULO COMANDOS--------MODULO COMANDOS--------------------------------------

#Crear imagen con la AI
def Bot_GPT_Img(string, email):
    try:
        # Configurar la API key de OpenAI
        openai.api_key = ai_token
        # Generar la imagen utilizando DALL-E
        response = openai.Image.create(
        prompt=string,
        n=1,
        size="512x512"
        )
        # Obtener la URL de la imagen generada
        image_url = response['data'][0]['url']
        # Descargar la imagen y mostrarla en Python
        image_data = requests.get(image_url).content
        image = Image.open(BytesIO(image_data))
        # Guardar la imagen en formato JPEG
        image.save("imagen_generada.jpg", "JPEG")
        mail ('imagen_generada.jpg','adj',email)
    except:
        mail ('No se pudo generar la imagen', 'txt', email)





def Img(string, email):
    # Realizar la búsqueda en Bing
    nombre = string.replace(' ', '+')
    url = f"https://www.bing.com/images/search?q={nombre}"
    response = requests.get(url)
    response.raise_for_status()

    # Obtener los enlaces de las imágenes encontradas
    enlaces_imagenes = response.text.split('murl&quot;:&quot;')[1:]

    # Seleccionar al azar las imágenes descargadas
    imagenes_seleccionadas = random.sample(enlaces_imagenes, min( 3, len(enlaces_imagenes)))

    # Descargar las imágenes seleccionadas
    nombres_imagenes = []
    for i, imagen in enumerate(imagenes_seleccionadas):
        response = requests.get(imagen.split('&quot;')[0])
        response.raise_for_status()
        nombre_imagen = f"{nombre}_{i+1}.jpg"  # Puedes ajustar la extensión según el formato de las imágenes
        with open(nombre_imagen, "wb") as archivo:
            archivo.write(response.content)
        nombres_imagenes.append(nombre_imagen)

    print(nombres_imagenes)
    MultiEnvio(nombres_imagenes, email)
    mail('Completado!!, Espero te sirvan. ', 'text', email)




def Img2(nombre, email):
     # Realizar la búsqueda en Bing
    url = f"https://www.bing.com/images/search?q={nombre}"
    response = requests.get(url)
    response.raise_for_status()

    # Obtener los enlaces de las imágenes encontradas
    soup = BeautifulSoup(response.text, "html.parser")
    enlaces_imagenes = [img.get("src") for img in soup.find_all("img") if img.get("src")]

    # Seleccionar al azar las imágenes descargadas
    imagenes_seleccionadas = random.sample(enlaces_imagenes, min(4, len(enlaces_imagenes)))


    # Descargar las imágenes seleccionadas
    nombres_imagenes = []
    for i, imagen in enumerate(imagenes_seleccionadas):
        response = requests.get(imagen)
        response.raise_for_status()
        nombre_imagen = f"{nombre}_{i+1}.jpg"  # Puedes ajustar la extensión según el formato de las imágenes
        with open(nombre_imagen, "wb") as archivo:
            archivo.write(response.content)
        nombres_imagenes.append(nombre_imagen)

    MultiEnvio(nombres_imagenes, email)
    mail('Completado!!, Espero te sirvan. ', 'text', email)




#Contactar al creador
def AcercaDe(string, email):
    texto_x = '''
    Mi creador es YoandyC
    '''
    mail (texto_x, 'text', email)



#si esta vacío enviamos eco, de lo contrario el eco de la palabra
def Echo(string, email):
    if string == '?':
        mail ('Estoy activo!!!', 'text', email)
    else:
        mail (string, 'text', email)



# Mostrando los comandos disponibles
def Help(string, email):
    Ayuda = '''
    Los comandos disponibles son:\n
    /ayuda Presenta esta ayuda.\n
    /eco Comando para saber si el bot se encuentra activo.\n
    /bot Realiza una pregunta al bot.(No exceder los 500 caracteres)\n
    /web Busca una palabra, frase o dirección URL en la web devolviendo la página html asociada.\n
    /img Descarga 3 imágenes al azar de la web relacionadas a un nombre de búsqueda.\n
    /descarga Descarga un archivo desde una URL dividiéndolo en partes de 10Mb.\n
    /youtube Descarga un video desde YouTube con resolución de 360p.\n
    /reporte Crea un reporte de errores encontrados, o solicitudes al creador.\n
    Nota: No abusen que soy nuevo :)
    '''
    mail (Ayuda, 'text', email)
#/descarga Descarga un archivo desde una URL.\n

#recordar una ayuda diferente a los usuarios claro... :)
def AdminHelp(string, email):
    Ayuda = '''
    Los comandos disponibles son:\n
    /ayuda Presenta esta ayuda.\n
    /eco Comando para saber si el bot se encuentra activo.\n
    /contacto Muestra el creador (solo con fines de pruebas).\n
    /reporte Agrega un reporte (solo con fines de pruebas).\n
    /leer Lee los reportes echos por los usuarios.\n
    /listar Lista archivos olvidados en el bot.\n
    /elimina Elimina un archivo o archivos de los obtenidos en el comando anterior (archivo1, archivo2, archivo3)\n
    /bot Realiza una pregunta al bot.(No exceder los 500 caracteres)\n
    /botimg Crea una imagen con AI desde una descripción\n
    /web Busca una palabra, frase o dirección URL en la web devolviendo la página html asociada.\n
    /img Descarga 3 imágenes al azar de la web relacionadas a un nombre de búsqueda.\n 
    /descarga Descarga un archivo desde una URL.\n
    /descarga2 Descarga un archivo desde una URL dividiéndolo en partes de 10Mb.\n
    /youtube Descarga un video desde YouTube con resolución de 360p.
    '''
    mail (Ayuda, 'text', email)



#si esta vacío solicitamos entre algo y sugerimos con ayuda
#de lo contrario verificamos si es una url o solo texto
def Buscador(string, email):
    # Verificar si el parámetro está vacío
    if not string:
        mail ("Debe ingresar una palabra, frase o URL.",'text', email)
    else:
        # Verificar si la entrada es una URL
        if string.startswith("http"):
            try:
                # Obtener el HTML de la URL
                response = requests.get(string)
                html = response.text
            except requests.exceptions.RequestException as e:
                # Manejar la excepción y retornar un mensaje al usuario
                mail (f"No se pudo obtener la página web: {str(e)}",'text', email)
        else:
            # Realizar la búsqueda en Google
            query = string.replace(" ", "+")
            url = f"https://google.com/search?client=opera&q={query}"
            try:
                response = requests.get(url)
                html = response.text
            except requests.exceptions.RequestException as e:
                # Manejar la excepción y retornar un mensaje al usuario
                mail (f"No se pudo realizar la búsqueda: {str(e)}",'text', email)

        # Modificar los enlaces de la página web
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.find_all("a", href=True):
            if link["href"].startswith("http"):
                email_body = f"/web {link['href']}"
                link["href"] = f"mailto:{radr}?body={urllib.parse.quote(email_body)}"
            else:
                # Convertir URL relativa a completa
                base_url = "https://www.google.com"
                complete_url = urllib.parse.urljoin(base_url, link["href"])
                email_body = f"/web {complete_url}"
                link["href"] = f"mailto:{radr}?body={urllib.parse.quote(email_body)}"

    # Retornar la HTML resultante
    mail (str(soup), 'html', email)



#Chat con la AI
def Bot_GPT(string, email):

    if len(string)>500:
        mail ('Lo sentimos, la solicitud no debe exceder los 500 caracteres.', 'text', email)
    else:

        def get_response(user_input):
            split_message = re.split(r'\s|[,:;.?!-_]\s*', user_input.lower())
            response = check_all_messages(split_message)
            return response

        def message_probability(user_message, recognized_words, single_response=False, required_word=[]):
            message_certainty = 0
            has_required_words = True

            for word in user_message:
                if word in recognized_words:
                    message_certainty +=1

            percentage = float(message_certainty) / float (len(recognized_words))

            for word in required_word:
                if word not in user_message:
                    has_required_words = False
                    break
            if has_required_words or single_response:
                return int(percentage * 100)
            else:
                return 0

        def check_all_messages(message):
                highest_prob = {}

                def response(bot_response, list_of_words, single_response = False, required_words = []):
                    nonlocal highest_prob
                    highest_prob[bot_response] = message_probability(message, list_of_words, single_response, required_words)

                response('Hola', ['hola', 'klk', 'saludos', 'buenas', 'hi'], single_response = True)
                response('Siempre a la orden', ['gracias', 'te lo agradezco', 'thanks'], single_response=True)
                #response('En optimas condiciones para trabajar, si puedo ayudarte en algo?', ['como', 'estas', 'va', 'vas', 'sientes'], required_words=['como'])
                response('Mi creador es Yoandy Calvelo?', ['creador', 'programo', 'programó'], required_words=['quien'])
                response('No se me permite hablas de ese tema', ['porno', 'pornografia', 'pornografico', 'pornografía', 'pornográfico','sexo', 'xxx', 'desnudas', 'desnudos'], single_response=True)


                best_match = max(highest_prob, key=highest_prob.get)
                #print(highest_prob)

                def unknown(string):
                    openai.api_key = ai_token

                    # Agrega el mensaje a la conversación
                    conversation.append(string)
                    # Si la conversación tiene más de 20 mensajes
                    # elimina el mensaje más antiguo
                    if len(conversation) > 6:
                        conversation.pop(0)

                    # Concatena los mensajes anteriores para crear un contexto
                    context = '\n'.join(conversation)
                    print(f"{context}\n {string}\nBot:")
                    try:
                        # llamada a la respuesta
                        response = openai.Completion.create(
                            engine="text-davinci-003",
                            prompt=(f"{context}\n {string}\nBot:"),
                            max_tokens=1024,
                            temperature=0.5,
                            top_p=1,
                            frequency_penalty=0,
                            presence_penalty=0,
                        )
                        # Agrega la respuesta a la conversación
                        bot_response = response.choices[0].text.strip()
                        conversation.append(bot_response)

                        return(bot_response)
                        #return(response.choices[0].text,'text')
                    except:
                        mail("Se ha agotado la cuota de la API de ChatGPT.", 'text', email)

                return unknown(string) if highest_prob[best_match] < 1 else best_match
        mail (str(get_response(string)),'text', email)



#Añadiendo el reporte
def Report(string, email):
    # Verificar si el archivo existe
    if not os.path.isfile("Reporte.txt"):
        # Si el archivo no existe, crearlo y agregar el texto
        with open("Reporte.txt", "w") as archivo:
            archivo.write(email+': '+string)
    else:
        # Si el archivo existe, agregar el texto al final
        with open("Reporte.txt", "a") as archivo:
            archivo.write("\n\n"+email+': '+ string)
    mail ('Reporte realizado con éxito.', 'text', email)



#leer los reportes realizados
def Leer_Report(string, email):
    # Verificar si el archivo existe
    if os.path.isfile('Reporte.txt'):
    # Si el archivo existe, leer su contenido
        with open('Reporte.txt', 'r') as archivo:
            contenido = archivo.read()
            mail (contenido, 'text', email)
            # Eliminar el archivo
            os.remove('Reporte.txt')
    else:
        # Si el archivo no existe, informarlo
        mail ('No existe ningún reporte.', 'text', email)


    

#********************************************************
                
def ListaDir():
    lista =  []
    archivos_app = ['BotNav.py', 'conexion.py', 'config.py', 'requirements.txt']   
    nombres_archivos = os.listdir()   
    for archivo in nombres_archivos:
        if archivo not in archivos_app:
            lista.append(archivo)
    print ('Archivo descargado:')
    print (lista)        
    return (lista)



# Compactamos el archivo q le pasemos
def Compacta(archivo):
    subprocess.run(['py7zr', 'c', '-v15m', f'{archivo}.7z', archivo])
    os.remove(archivo)




def DescargaArchivo():
    while True:
        if cola_descarga.empty():
            print('Cola vacía')
            break
        
        print('Preparando la descarga.')
        descarga = cola_descarga.get()
        url = descarga[0]
        email = descarga[1]
    
        
        palabras_prohibidas = ["youtube", "porno", "sexo", "calentitas"]  # Palabras clave a filtrar
        url = url.lower()
        # Comprobar si la URL contiene alguna palabra clave prohibida
        for palabra in palabras_prohibidas:
            if palabra in url:
                mail ("URL no permitida", 'text', email)
                break  
        
        try:
            mail('Descargando el archivo...', 'text', email)                       
            subprocess.run(['download-easy', url])
            # Nombre de archivo descargado
            nombre_archivo = ListaDir() 
            Compacta(nombre_archivo[0])      
            # Recuperamos los volúmenes creados
            archivos_creados = ListaDir()

            MultiEnvio(archivos_creados, email)
            mail ('Descarga terminada!!!', 'text', email) 
            
        except OSError as e:
            print(f'Algo paso error: {str(e)}')
            mail (f'Error al descargar el archivo: {str(e)}', 'text', email)
            
        # Marcar la tarea como completada
        cola_descarga.task_done()

#********************************************************

def DescargaYoutube():    
    while True:
        if cola_youtube.empty():
            break
        descarga = cola_youtube.get()
        url = descarga[0]
        email = descarga[1]
        try:
            video = YouTube(url, use_oauth=False, allow_oauth_cache=True)
            # Buscar la resolución 360p y, si no está disponible, la siguiente resolución de mayor calidad
            resolucion = "360p"
            if resolucion not in video.streams.filter(progressive=True).all():       
            # Buscar la siguiente resolución disponible
                resolucion = video.streams.filter(progressive=True).all()[0].resolution

            # Descargar el video con la resolución seleccionada
            video.streams.filter(progressive=True, resolution=resolucion).first().download()
            compactados = Compacta(video.title)
            MultiEnvio(compactados, email)
        except VideoUnavailable as e:
           mail(f"El video no está disponible. Error {str(e)}",'text',email)       

        cola_youtube.task_done()  
        
                    
    
    
def agregar_url_a_cola_youtube(url, email):
    global subproceso_youtube
    cola_youtube.put((url, email))   
    mail(f'Solicitud de descarga añadida a la cola.\n{url}','text', email)   
    if subproceso_youtube is None or not subproceso_youtube.is_alive():
        # Crear y ejecutar el subproceso
        subproceso_youtube = threading.Thread(target=DescargaYoutube)
        subproceso_youtube.start()
        

"""
def agregar_url_a_cola_descarga(url, email):
    global subproceso_descarga   
    cola_descarga.put((url, email))
    mail(f'Solicitud de descarga añadida a la cola.\n{url}','text', email)
    if subproceso_descarga is None or not subproceso_descarga.is_alive():
        # Crear y ejecutar el subproceso solo si no hay otro subproceso en ejecución
        subproceso_descarga = threading.Thread(target=DescargaArchivo)
        subproceso_descarga.start()
  """      
        


 #Agregando las url a la cola mediante la función
def run_DescargaArchivo(url, email):
    #agregar_url_a_cola_descarga(url,email)
    global subproceso_descarga   
    cola_descarga.put((url, email))
    mail(f'Solicitud de descarga añadida a la cola.\n{url}','text', email)
    if subproceso_descarga is None or not subproceso_descarga.is_alive():
        # Crear y ejecutar el subproceso solo si no hay otro subproceso en ejecución
        subproceso_descarga = threading.Thread(target=DescargaArchivo)
        subproceso_descarga.start()
    
    
def run_DescargaYoutube(url, email):
    agregar_url_a_cola_youtube(url,email)
    


#Ejecutamos un Hilo por cada entrada de búsqueda
def run_Buscador(string, email):
    rb = Multihilos2(target=Buscador, args=(string, Semail))
    rb.start()
    rb.join()
    return rb.result

#Ejecutamos un Hilo por cada entrada de búsqueda
def run_BotIMG(string, email):
    rbi = Multihilos2(target=Bot_GPT_Img, args=(string, email))
    rbi.start()
    rbi.join()
    return rbi.result

def run_Img(string, email):
    rimg = Multihilos2(target=Img, args=(string, email))
    rimg.start()
    rimg.join()
    return rimg.result



#Clase para crear multi tareas con hilos de ejecución
class Multihilos2(threading.Thread):
    def __init__(self, target, args=()):
        super().__init__(target=target, args=args)
        self._result = None

    def run(self):
        self._result = self._target(*self._args)

    @property
    def result(self):
        return self._result



def Archivos_olvidados(string, email):
    lista = []
    lista = ListaDir()        
    texto_listado = ""
    for elemento in lista:
        texto_listado += elemento + "\n"                   
    mail(texto_listado,'text', email)
    
    

def Elimina_archivos(string, email):
    archivos = string.split(", ")
    lista = ['Archivos eliminados:']
    for archivo in archivos:
        if os.path.exists(mi_dir+'\\'+archivo):
            os.remove(archivo)
            lista.append(archivo)
        
    mail('Archivos eliminados!!','text', email) 



#Comando para los usuarios
commands = {
    '/contacto':AcercaDe,
    '/eco': Echo,
    '/ayuda': Help,
    '/reporte':Report,
    '/botimg':run_BotIMG,
    '/bot':Bot_GPT,
    '/descarga':run_DescargaArchivo,
    '/img':run_Img,
    '/youtube':run_DescargaYoutube    
}

#Comando para los administradores
admincommand = {
    '/contacto':AcercaDe,
    '/eco': Echo,
    '/ayuda': AdminHelp,
    '/reporte':Report,
    '/leer':Leer_Report,
    '/listar': Archivos_olvidados,
    '/elimina':Elimina_archivos,  
    '/web': run_Buscador,
    '/bot':Bot_GPT,
    '/botimg':run_BotIMG,
    '/descarga':run_DescargaArchivo,
    '/img':run_Img,
    '/youtube':run_DescargaYoutube
}

#---------TERMINA MODULO COMANDOS-------------------------------------------------------



def imap_init():
    #print(pwd)
    global i
    i = imapclient.IMAPClient(imapserver)
    c = i.login(radr, pwd)
    i.select_folder('INBOX')


def smtp_init():
    global s
    s = smtplib.SMTP(smtpserver, smtpserverport,timeout=60) #quitar _SSL para gmail
    c = s.starttls()[0]
    if c != 220: # if c is not 220
        raise Exception('Conexión tls fallida: ' + str(c))
    c = s.login(radr, pwd)[0]
    if c != 235: # if c is not 235
        raise Exception('SMTP login fallido: ' + str(c))


def get_unread():
    global i
    imap_init()
    i.select_folder('INBOX')
    uids = i.search(['UNSEEN'])
    if not uids:
        return None #no hay mensajes disponibles
    else:
        #print("Encontrados %s Sin leer" % len(uids))
        return i.fetch(uids, ['BODY[]', 'FLAGS']) #retornamos el mensaje y lo marco como leído


def mail(text, tipo, email):   
    global s
    smtp_init()
    msg = MIMEMultipart()
    msg['From'] = radr
    msg['To'] = email
    msg['Subject'] = ""
    # print('mensaje saliente:'+ cliente)
    if tipo == 'text':
        msg_p = MIMEText(text, 'plain')
    elif tipo == 'html':
        msg_p = MIMEText(text, 'html')
        msg_p.add_header('content-disposition', 'attachment', filename='web_index.html')
    elif tipo == 'img':
        msg_p = MIMEText(text, 'plain')
        msg_p.add_header('content-disposition', 'attachment', filename=text)
    elif tipo == 'adj':
        archivo_adjunto = open(text, 'rb')
        msg_p = MIMEText('Archivo: '+text, 'html')
        msg_p = MIMEBase('application', "octet-stream")
        msg_p.set_payload(archivo_adjunto.read())
        encoders.encode_base64(msg_p)
        msg_p.add_header('Content-Disposition', 'attachment; filename="{}"'.format(basename(text)))
    elif tipo == 'pdf':
        with open(text, 'rb') as f:
            pdf_data = f.read()
        msg.attach(MIMEText('Encontrada la hoja de datos del: '+text, 'html'))#plain
        msg_p = MIMEApplication(pdf_data, Name=text)
        msg_p['Content-Disposition'] = f'attachment; filename={text}'

    msg.attach(msg_p)
    s.sendmail(radr, email, msg.as_string())
    s.close()
    if os.path.exists(text) and (tipo == 'adj'):
        os.remove(text)
    try:
        os.unlink(text)
    except:
        pass

#---------------------------------------------------------------------------
def MultiEnvio(files, email):
    # Loop del multi envío
    for file in files:
        smtp_init()
        # Creando el email
        msg = MIMEMultipart()
        msg['From'] = radr
        msg['To'] = email
        msg['Subject'] = ""
        #msg.attach(MIMEText('Instrucciones:\nAl descargar el archivo lo veras con extensión .dat\nGuárdalo con extensión .zip si lo permite o renómbralo después de guardado.\nAl  extraerlo si solicita una contraseña, utiliza:  bot'))

        # Adjuntando el archivo
        with open(file, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{file}"')
            msg.attach(part)

        s.sendmail(radr, email, msg.as_string())
        s.close()

    # Eliminando los archivos
    for file in files:
        if os.path.exists(file):
            os.remove(file)
#---------------------------------------------------------------------------


def analyze_msg(raws, a):
    global cliente
    global cmd
    msg = pyzmail.PyzMessage.factory(raws[a][b'BODY[]'])
    frm = msg.get_addresses('from')
    cliente = frm[0][1]

    # Get text from message and remove signature
    text = msg.text_part.get_payload().decode(msg.text_part.charset)
    text = re.sub(r'--\s*\n.*', '', text, flags=re.DOTALL)

    # Extract command from text
    match = re.search(r'^/(\w+)', text.strip())
    if match:
        cmd = '/'+match.group(1)
        print(cmd)
        if frm[0][1] != admin:

            if cmd not in commands:
                return False
            else:
                try:
                    arg = text.split(' ', 1)[1]
                    arg =  arg.replace("\n", "").strip()
                except IndexError:
                    arg = '?'
                return [cmd, arg, cliente]
        else:
            if cmd not in admincommand:
                return False
            else:
                try:
                    arg = text.split(' ', 1)[1]
                    arg =  arg.replace("\n", "").strip()
                except IndexError:
                    arg = '?'
                return [cmd, arg, cliente]
    else:
        return False




if __name__ == '__main__':
    print(f'Bot iniciado en ({radr})')
    imap_init()
    live()
    




while True:  # Revision constante
    print('En espera...')
    try:
        msgs = get_unread()
        while msgs is None:# si no hay esperamos un tiempo para revisar nuevamente
            time.sleep(check_freq)
            msgs = get_unread()# re intento
        for a in msgs.keys():
            if type(a) is not int:#Clasificarlo
                continue
            cmds = analyze_msg(msgs, a)#lo analizamos en busca e comandos
            if cmds is None:
                continue
            elif cmds is False:  # Comando no valido
                print('Comando no valido')
                Nota = 'Comando no valido\nEnvíe el comando /ayuda para ver una lista de los que se encuentran  disponibles.'
                mail(Nota, 'text', cliente) #enviamos un email de tipo texto"""
                continue
            else:
                if cliente != admin: #Salida para los clientes
                    print('USER: '+cliente)
                    commands[cmds[0]](cmds[1], cmds[2])
                else: #salida para el admin
                    print('ADMIN: '+cliente)
                    admincommand[cmds[0]](cmds[1], cmds[2])


    except OSError as e:
        print("Error de tipo:", type(e).__name__)
        time.sleep(30)
        imap_init()
        continue
    except smtplib.SMTPServerDisconnected:
        print("Re intento de conexión en breve")
        time.sleep(30)
        imap_init()
        continue

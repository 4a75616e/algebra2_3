import tkinter as tk;
from tkinter import filedialog;
from PIL import Image, ImageTk;
from threading import Thread;
#import tres;
import time;
import sys
import numpy as np
#import os;

colorTema   = {"fondo":"#ADD8E6","entradas":"#CAE6EF"};
tamanoImg   = 400,400;
imgDefault  = "vacia.png";
fontDefault = ("Eras Light ITC",10);


termino = False;

def sign(p1, p2, p3):
  return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])


def PointInAABB(pt, c1, c2):
  return c2[0] <= pt[0] <= c1[0] and \
		 c2[1] <= pt[1] <= c1[1]

def PointInTriangle(pt, v1, v2, v3):
	b1 = sign(pt, v1, v2) < 0
	b2 = sign(pt, v2, v3) < 0
	b3 = sign(pt, v3, v1) < 0
	return ((b1 == b2) and (b2 == b3)) and \
		 PointInAABB(pt, list(map(max, v1, v2, v3)), list(map(min, v1, v2, v3)))


#dice si un punto esta dentro de un cuadrilatero
def punto_adentro(point,a,b,c,d,):
	return PointInTriangle(point,a,b,c) and PointInTriangle(point,c,d,a)


#multiplica la TL de una coordenada cartesiana
def multiplicar(matriz,puntos):
	resultado=[0,0]
	for fila in range(len(matriz)):
		for valor in range(len(matriz[fila])):
			resultado[fila]+=(matriz[fila][valor]*puntos[valor])
	return (resultado)


#aplica la tecnica del vecino mas cercano
def vecinos(imagen,buffer,oldwidth,oldheight,informacion,width,height,k):
	print(width,height)
	a = (buffer[0,0,0],buffer[0,0,1])
	b = (buffer[0,oldheight-1,0],buffer[0,oldheight-1,1])
	c = (buffer[oldwidth-1,oldheight-1,0],buffer[oldwidth-1,oldheight-1,1])
	d = (buffer[oldwidth-1,0,0],buffer[oldwidth-1,0,1])
	for fila in range(width):
		print(fila)
		for columna in range(height):
			if(not informacion[fila][columna]):
				punto=(fila,columna)
				if(not punto_adentro(punto,a,b,c,d)):
					encontradas=0
					valores=0
					separacion=1
					while(encontradas<k):
						for i in range(-1*separacion,separacion):
							for j in range(-1*separacion,separacion):
								if(fila+i>=0 and fila+i<width and columna+j>=0 and columna+j<height):
									if(informacion[fila+i][columna+j]):
									   valores+=imagen[fila+i,columna+j]
									   encontradas+=1
						separacion+=1
					
					valores=valores//encontradas
					imagen[fila,columna]=valores
	return imagen


#x0,y0 son los puntos que se tomaran como el punto 0,0
#interpolar es un booleano que indica si se aplicara interpolacion a la imagen transformada
#tl es la matriz de orden 2
#img_path es el path de la imagen
def transformar(tl,img_path,x0,y0,interpolar):
	global termino;
	termino = False
	img = Image.open(img_path).convert('L')
	img.load()
	imagen=np.asarray(img,dtype="int32")
	width,height=imagen.shape[0],imagen.shape[1]
	buffer=np.zeros((width,height,2),dtype="int32")
	xmax=ymax=-1
	xmin=ymin=sys.maxsize
	for fila in range(width):
		for columna in range(height):
			transformacion=multiplicar(tl,(fila-x0,columna-y0))
			x=int(transformacion[0])
			y=int(transformacion[1])
			if(x>xmax):
				xmax=x
			if(x<xmin):
				xmin=x
			if(y>ymax):
				ymax=y
			if(y<ymin):
				ymin=y
			buffer[fila,columna]=[x,y]
	nuevowidth=xmax-xmin
	nuevoheight=ymax-ymin
	informacion_interpolacion=[[False for j in range(nuevoheight)] for i in range(nuevowidth)]
	transformada=np.zeros((nuevowidth,nuevoheight),dtype="int32")
	for fila in range(width):
		for columna in range(height):
			#lo normaliza para que quede en un valor>=0
			nx=buffer[fila,columna,0]-xmin-1
			ny=buffer[fila,columna,1]-ymin-1
			color=imagen[fila,columna]
			transformada[nx,ny]=color
			informacion_interpolacion[nx][ny]=True
	if(interpolar):
		transformada=vecinos(transformada,buffer,width,height,informacion_interpolacion,nuevowidth,nuevoheight,2)
	im=Image.fromarray(transformada)
	#im.show()
	im=im.convert("L")
	im.save("res.png")
	print("Saleeee")
	termino = True



###################################################################################
#########################################INTERFAZ##################################
###################################################################################

def intro(ventana):
	#global marco
	marco        = tk.Frame(ventana, width=1000, height=1000, bg=colorTema["fondo"]);
	label_nombre = tk.Label(marco,text="Transformaciones Lineales Aplicadas a\nImágenes Digitales",fg="red", 
		bg=colorTema["fondo"],font=(fontDefault[0],30));
	boton_main   = tk.Button(marco,text="Iniciar",command=lambda: abrirMain(ventana,marco),height=2,width=12,font=("Arial",20));
	label_nombre.place(x=150,y=100);
	boton_main.place(x=400, y=300);
	marco.pack();
	return;



def abrirMain(ventana,marco):
	marco.destroy();
	main(ventana);
	return;



def abrirImagen(marco):
	path_imagen = filedialog.askopenfilename(title="Seleccionar imagen");
	print(path_imagen);

	marco.path_imagenStringVar.set(path_imagen);
	marco.path_imagen = path_imagen;

	marco.boton_cargarImagen.configure(state=tk.NORMAL);
	colocarImagenOriginal(marco)
	return path_imagen;



def colocarImagenOriginal(marco):
	image = Image.open(marco.path_imagen);
	image = image.resize(tamanoImg, Image.ANTIALIAS);
	img = ImageTk.PhotoImage(image);

	marco.panelImagenOriginal.configure(image=img);
	marco.panelImagenOriginal.image = img;
	return;



def colocarImagenTransformada(marco,i=0):
	global termino;
	marco.panelCargandoTexto.configure(text="Cargando...");
	if termino:
		image = Image.open("res.png");
		image = image.resize(tamanoImg, Image.ANTIALIAS);
		img = ImageTk.PhotoImage(image);
		marco.panelImagenTransformada.configure(image=img);
		marco.panelImagenTransformada.image = img;
		marco.panelCargandoTexto.configure(text="");
	else:
		marcoActual = marco.gifCargando[i];
		i += 1;
		marco.panelCargando.configure(image=marcoActual);
		print("DUERMEEE");
		if i == 60:
			i = 0;
		marco.after(100, colocarImagenTransformada, marco, i);
	



def validar(accion, indice, valorHipotetico, valorPrevio, valorInsertado, tipoValidacion, tipoTrigger, nombreWidget):
	if accion != "0":
		if valorInsertado in "-0123456789":
			return True
		return False;
	return True;



def aplicarTransformacion(marco, interpolar=False):
	matricita = [[0,0],
				 [0,0]];

	if marco.texto_matrizEntradas[0].get() == "":
		matricita[0][0] = 0;
	else:
		matricita[0][1] = int(marco.texto_matrizEntradas[0].get());

	if marco.texto_matrizEntradas[1].get() == "":
		matricita[0][1] = 0;
	else:
		matricita[0][1] = int(marco.texto_matrizEntradas[1].get());

	if marco.texto_matrizEntradas[2].get() == "":
		matricita[1][0] = 0;
	else:
		matricita[1][0] = int(marco.texto_matrizEntradas[2].get());

	if marco.texto_matrizEntradas[3].get() == "":
		matricita[1][1] = 0;
	else:
		matricita[1][1] = int(marco.texto_matrizEntradas[3].get());

	print(matricita);

	hilo = Thread(target=transformar, args=(matricita,marco.path_imagen,0,0,interpolar));
	hilo.start();
	#tres.transformar(matricita,marco.path_imagen,0,0,interpolar)

	hilo2 = Thread(target=colocarImagenTransformada, args=(marco,0));
	hilo2.start();
	"""
	FALTA UN TRY CATCH PARA CUANDO LA MATRIZ DE TR ES NULA
	"""
	return;


def actualizarGif(i):
	marcoActual = gifCargando[i]
	ind += 1
	label.configure(image=marcoActual)
	root.after(100, actualizarGif, i)



def main(ventana):
	ventana.geometry("1000x700+100+0");
	marco = tk.Frame(ventana, width=1000, height=1000, bg=colorTema["fondo"]);
	marco.pack();
	###############################################################################
	#Coloca imagenes vacias
	label_nombreImagenOriginal = tk.Label(marco, text = "Imagen Original", bg=colorTema["fondo"],font=fontDefault);
	label_nombreImagenOriginal.place(x=140,y=0);

	
	img = Image.open("vacia.png");
	img = img.resize(tamanoImg, Image.ANTIALIAS);
	img = ImageTk.PhotoImage(img);
	panelImagenOriginal = tk.Label(marco, image=img, bg=colorTema["fondo"]);
	panelImagenOriginal.image = img;
	panelImagenOriginal.place(x=50,y=20);
	marco.panelImagenOriginal = panelImagenOriginal;

	label_nombreImagenTransformada = tk.Label(marco, text = "Imagen Transformada", bg=colorTema["fondo"],font=fontDefault);
	label_nombreImagenTransformada.place(x=720,y=0);
	img = Image.open("vacia.png");
	img = img.resize(tamanoImg, Image.ANTIALIAS);
	img = ImageTk.PhotoImage(img);
	panelImagenTransformada = tk.Label(marco, image=img, bg=colorTema["fondo"]);
	panelImagenTransformada.image = img;
	panelImagenTransformada.place(x=550,y=20);
	marco.panelImagenTransformada = panelImagenTransformada;

	###############################################################################
	#Colocar separadores
	separador_horizontal1 = tk.Frame(relief=tk.RIDGE, bg="black",width=1000, height=1);
	separador_horizontal2 = tk.Frame(relief=tk.RIDGE, bg="black",width=1000, height=1);
	separador_vertical    = tk.Frame(relief=tk.RIDGE, bg="black",width=1,height=440);
	separador_horizontal1.place(x=0,y=440);
	separador_horizontal2.place(x=0,y=540);
	separador_vertical.place(x=500, y=0);
	###############################################################################
	#Colocar buscar imagen
	label_buscarImagen = tk.Label(marco, text="Buscar Archivo de Imagen:", bg=colorTema["fondo"], font=fontDefault);
	label_buscarImagen.place(x=20,y=460);

	path_imagenStringVar = tk.StringVar();
	entry_buscarImagen = tk.Entry(marco, textvariable=path_imagenStringVar,font=fontDefault,
		state=tk.DISABLED,width=81,bd=5,bg=colorTema["entradas"],selectbackground=colorTema["entradas"]);
	entry_buscarImagen.place(x=20,y=480);
	marco.path_imagenStringVar = path_imagenStringVar;

	boton_buscarImagen = tk.Button(marco,text="Examinar", font=fontDefault, bg=colorTema["fondo"], 
		command=lambda:abrirImagen(marco));
	boton_buscarImagen.place(x=765,y=480);
	boton_cargarImagen = tk.Button(marco,text="Cargar Imagen", font=fontDefault, bg=colorTema["fondo"], 
		command=lambda:colocarImagenOriginal(marco), state=tk.DISABLED);
	boton_cargarImagen.place(x=860,y=480);
	marco.boton_cargarImagen = boton_cargarImagen;

	###############################################################################
	#Colocar zona matriz
	label_buscarImagen = tk.Label(marco, text="Insertar Matriz de la Transformación", bg=colorTema["fondo"], font=fontDefault);
	label_buscarImagen.place(x=20,y=560);

	texto_matrizEntradas = [tk.StringVar() for i in range(4)];

	matrizEntradas = [tk.Entry(marco, validate = 'key', width=3, font=fontDefault, justify=tk.CENTER, 
		textvariable=texto_matrizEntradas[i]) for i in range(4)];

	marco.texto_matrizEntradas = texto_matrizEntradas;

	for i in matrizEntradas:
		i['validatecommand'] = (i.register(validar),"%d", "%i", "%P", "%s", "%S", "%v", "%V", "%W");

	matrizEntradas[0].place(x=130,y=595);
	matrizEntradas[1].place(x=165,y=595);
	matrizEntradas[2].place(x=130,y=620);
	matrizEntradas[3].place(x=165,y=620);

	boton_aplicarTransformacion = tk.Button(marco, text="Aplicar Transformación", bg=colorTema["fondo"], font=fontDefault, 
		command=lambda:aplicarTransformacion(marco));
	boton_aplicarTransformacion.place(x=300,y=590);

	boton_aplicarTransformacionInterpolacion = tk.Button(marco, text="Aplicar Transformación con Interpolación", 
		bg=colorTema["fondo"], font=fontDefault, command=lambda:aplicarTransformacion(marco, interpolar=True));
	boton_aplicarTransformacionInterpolacion.place(x=300,y=620);

	scale_w = 60/400;
	scale_h = 60/400;
	#photoImg.zoom(scale_w, scale_h);

	marco.gifCargando = [None for i in range(60)];
	for i in range(60):
		marco.gifCargando[i] = tk.PhotoImage(file='cargando120x120.gif',format = 'gif -index %i' %(i));
		#marco.gifCargando[i].zoom(6);
		#marco.gifCargando[i].subsample(40);

	panelCargando = tk.Label(marco, bg=colorTema["fondo"]);
	panelCargandoTexto = tk.Label(marco, bg=colorTema["fondo"],font=fontDefault);
	panelCargandoTexto.place(x=880,y=660);
	panelCargando.place(x=880,y=560);
	marco.panelCargando = panelCargando;
	marco.panelCargandoTexto = panelCargandoTexto;

	###############################################################################
	#Menu
	menubar = tk.Menu(ventana);
	filemenu = tk.Menu(menubar, tearoff=0);
	filemenu.add_command(label="Abrir Imagen", command=lambda:abrirImagen(marco));
	filemenu.add_separator();
	filemenu.add_command(label="Salir", command=ventana.quit);
	menubar.add_cascade(label="File", menu=filemenu);
	ventana.config(menu=menubar);

	return;



#if os.name == 'nt':


ventana=tk.Tk();
ventana.geometry("1000x400+100+100");
ventana.title("Transformaciones Lineales Aplicadas a Imágenes Digitales.");
ventana.config(bg=colorTema["fondo"]);
ventana.resizable(width=False, height=False);
#Imagenes Cargadas#
#ropa=load_image("ropa.png") #Para cargar imagen#
####
intro(ventana);
ventana.mainloop();
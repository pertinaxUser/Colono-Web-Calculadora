#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import paginas.manejo.configuracion as conf
import paginas.manejo.formatoImagen as formatosI
import paginas.manejo.reporte as rep
import paginas.manejo.vistaImagenResultados as vistIR
import paginas.manejo.CONSTANTS as CONSTANTS
import paginas.manejo.savePDF as savePDF

from django.shortcuts import render, HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
from io import BytesIO
from paginas.manejo.conteoGeo import ConteoGeo

from .forms import UploadFileForm, Parametros

"""
Lanza la pagina principal
"""
def index(request):
    return render(request,'paginas/home.html')

"""
Lanza la pagina con la imagen cargada
"""
def cargado(request):
    return render(request,'paginas/imagCarga.html')

def cargadoConImagenO(request):
    return render(request,'paginas/imagCarga2.html')

def imagenO(request):
    logo={'c':'paginaP/img/imagTempW.tif'}
    return render(request,'paginas/imagSeleccion.html',logo)

"""
Lanza pagina con el formulario de cargado de imagen
"""
def formularioImagen(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        copiaImagenServidor(request.FILES['archivo'])
        imagenTif=ConteoGeo('paginas\static\paginaP\img\imagTempW.tif',50000000)
        imagenTif.escalar_imagen(400,400,'paginas\static\paginaP\img\imagTempW.jpg')
        temI=cv2.imread('paginas\static\paginaP\img\imagTempW.jpg')
        formatosI.cambio ( temI, "imagTempW.jpg" )
        #dor.dormir(5)
        return render(request,'paginas/imagCarga2.html')
    else:
        form = UploadFileForm()

    return render(request, 'paginas/cargarImg.html', {'form': form})

"""
Lanza procesamiento de la imagen, para luego presentar resultados.
"""
def prosesamiento(request):
    conteo=ConteoGeo('paginas\static\paginaP\img\imagTempW.tif',50000000)

    datos=conf.cargar()
    datos.datosString()

    print int(datos.ruido),float(datos.proximidad),"archivoshp",datos.nombreArchivo, datos.multiArchivo

    resultado=conteo.contadorAgrupado(int(datos.ruido),float(datos.proximidad),"paginas\\manejo\\archivoshp",
                                      str(datos.nombreArchivo), datos.multiArchivo)

    reporte=rep.Reporte( datos.escala, datos.ruido, datos.proximidad, datos.capacidad, resultado[1], resultado[0],
                         resultado[2], datos.multiArchivo,datos.nombreArchivo)

    vistIR.crearImgenResultados()

    resultado={'res': resultado[1],'tie':resultado[2],'cic':resultado[0], 'imgDraw':CONSTANTS.JPG_FULL_DIR}

    #datos.imp()
    rep.guardarReporte(reporte)
    return render(request,'paginas/imagProc2.html',resultado)

"""
Copia imagen cargada al servidor.
"""
def copiaImagenServidor(f):
    with open('paginas\static\paginaP\img\imagTempW.tif', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
"""
Lanza pagina con el formulario de ajuste de parametros.
"""
def ajusteParametros(request):
    if request.method == 'POST':
        if 'b1' in request.POST:
            conf.guardar(request.POST['escala'],request.POST['ruido'],request.POST['proximidad'],
                         request.POST['capacidad'], request.POST['multiArchivo'], request.POST['nombreArchivo'])
            return render(request,'paginas/home.html')
        elif 'b2' in request.POST:
            return render(request,'paginas/home.html')
        elif 'b3' in request.POST:
            carga=conf.predeterminado()
            form = Parametros(initial={'escala': carga.escala,'ruido':carga.ruido,'proximidad':carga.proximidad,
                                       'capacidad':carga.capacidad, 'multiArchivo':carga.multiArchivo,
                                       'nombreArchivo':carga.nombreArchivo})
            return render(request, 'paginas/ajustes.html', {'form': form})
        form = Parametros(request.POST, request.FILES)
        return render(request,'paginas/imagCarga2.html')
    else:
        carga=conf.cargar()
        form = Parametros ( initial={'escala': carga.escala, 'ruido': carga.ruido, 'proximidad': carga.proximidad,
                                     'capacidad': carga.capacidad, 'multiArchivo': carga.multiArchivo,
                                     'nombreArchivo': carga.nombreArchivo} )
    return render(request, 'paginas/ajustes.html', {'form': form})

"""Funcion que crea un PDF con los resultados y parametros con que se analizo la imagen """
def crearPDF(request):

    return savePDF.saveFilePDF()

def animacio(request):
    return render(request,'paginas/animacion.html')
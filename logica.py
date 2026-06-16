import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui, QtCore, uic
from PyQt5.QtWidgets import QGraphicsDropShadowEffect,QDialog
import math
from fpdf import FPDF
import subprocess

class ventanaHija(QDialog):
    def __init__(self,texto, parent=None):
        super(ventanaHija, self).__init__()
        self.setWindowFlag(Qt.FramelessWindowHint) #Ocultar barra superior
        self.setStyleSheet("QMainWindow{background-color: rgb(0, 0, 0)}")
        self.parent = parent
        self.texto = 'Selecciona el tipo de capa:'
        self.setWindowTitle("Numero de capa")
        self.setFixedSize(600,400)
        self.TypeCapa()
    def TypeCapa(self):
        self.fondo=QFrame(self)
        self.fondo.setGeometry(15,15,570,370)
        self.fondo.setStyleSheet('background-color:rgb(0, 0, 0);border-radius:5px')
        #boton cerrar de la ventana
        self.cerrar=QPushButton('X',self)


        
        self.cerrar.setGeometry(540,30,30,30)
        self.cerrar.setStyleSheet('QPushButton::hover''{''background-color: #ff5a97''}')
        self.cerrar.setCursor(Qt.PointingHandCursor) #Para poner el punto como una mano
        self.cerrar.clicked.connect(self.Cerrar)
        self.SelectCapa = QLabel('Hola',self)
        self.SelectCapa.setText(self.texto)
        self.SelectCapa.setGeometry(20, 20, 120, 25)
        self.SelectCapa.setStyleSheet('color:rgb(0, 0, 0);font-size: 12px;font-weight: bold;font-family: "Fantasy";')
        self.Type_cap=QComboBox(self)
        self.Type_cap.setGeometry(200,20,200,25)
        self.Type_cap.addItems(['Base granular','Sub-Base','Base tratada - Cemento','Base tratada - Asfalto'])
        #self.Confiabilidad.currentIndexChanged.connect(self.valor)
    def Cerrar(self):
        self.close()


class MainApp(QMainWindow):
    def __init__(self, parent=None, *args):
        super(MainApp, self).__init__(parent=parent)
        self.setStyleSheet("QMainWindow{background-color: rgb(241, 242, 243)}")
        self.setWindowFlag(Qt.FramelessWindowHint) #Ocultar barra superior
        self.setMinimumSize(1000,550)
        self.setMaximumSize(1000,550)
        self.setWindowTitle('Diseño de Pavimento')
        self.Formulario()
        self.menu()
        self.BarraInf()
        self.Resultado()
        self.Capas()
        #Abre el cuadro de dialogo
    def show_dialog(self):
        # Obtener texto del QLineEdit
        texto = 'hola'
        # Llamar la ventana hija pasandole un parametro
        ventanaHija(texto, self).exec_()
    def PDFGen(self):
        self.Resol()
        pdf = FPDF('P', 'mm', 'Letter')
        a=str(self.W18A.text())
        Zr=str(self.ZrA.text())
        So=str(self.SoA.text())
        DPSI=str(self.PSIA.text())
        pdf.add_page()
        pdf.set_font('helvetica', 'BIU', 16)
        pdf.set_text_color(0,0,0)
        pdf.set_font('times', '', 12)
        pdf.text(30, 10, 'Reporte de pavimento')
        pdf.text(30, 30, 'Numero de ejes equivalentes: '+a)
        pdf.text(30, 35, 'Confiabilidad (Zr): '+Zr)
        pdf.text(30, 40, 'Desviacion estandar (So): '+So)
        pdf.text(30, 45, 'Delta de serviciabilidad: '+DPSI)
        i=self.NCapa.currentIndex()
        if i==0:
            SN1=str(self.SN1.text())
            SN2=str(self.SN2.text())
            SN3=str(self.SN3.text())
            D1=str(self.e1.text())
            D2=str(self.e2.text())
            D3=str(self.e3.text())
            pdf.rect(x=120, y=55, w=40, h=5, style = 'F')
            pdf.text(163, 59, D1)
            pdf.text(30, 55, 'Numero estructural de la Subrasante: '+SN3)
            pdf.text(30, 60, 'Numero estructural de la Subase: '+SN2)
            pdf.text(30, 65, 'Numero estructural de la base: '+SN1)
            pdf.set_fill_color(150,150,150)
            pdf.rect(x=120, y=60, w=40, h=15, style = 'F')
            pdf.text(163, 70, D2)
            pdf.set_fill_color(50,85,15)
            pdf.rect(x=120, y=75, w=40, h=15, style = 'F')
            pdf.text(163, 85, D3)
        if i==1:
            SN1=str(self.SN1.text())
            SN3=str(self.SN3.text())
            D1=str(self.e1.text())
            D2=str(self.e2.text())
            pdf.rect(x=120, y=55, w=40, h=5, style = 'F')
            pdf.text(163, 59, D1)
            pdf.text(30, 55, 'Numero estructural de la Subrasante: '+SN3)
            pdf.text(30, 65, 'Numero estructural de la base: '+SN1)
            pdf.set_fill_color(150,150,150)
            pdf.rect(x=120, y=60, w=40, h=15, style = 'F')
            pdf.text(163, 70, D2)
        if i==2:
            SN3=str(self.SN3.text())
            D1=str(self.e1.text())
            pdf.rect(x=120, y=55, w=40, h=25, style = 'F')
            pdf.text(163, 70, D1)
            pdf.text(30, 55, 'Numero estructural de la Subrasante: '+SN3)
        pdf.output('pavimento%.pdf')
        path = 'pavimento%.pdf'
        subprocess.Popen([path], shell=True)
    #Funcion para cerrar la ventana
    def Cerrar(self):
        self.close()
    #Funcion para el menu lateral
    def menu(self):
        self.Lan=QLabel('AASHTO 93',self)
        self.Lan.setGeometry(65,65,150,20)
        self.Lan.setStyleSheet('color:rgb(80, 181, 255);font-size: 20px;font-weight: bold;font-family: "Fantasy";')
        self.SubT=QLabel('Pavimento flexible',self)
        self.SubT.setGeometry(81,85,150,20)
        self.SubT.setStyleSheet('color:rgb(180,180,180);font-size: 11px;font-family: "Fantasy";')
        self.op1=QPushButton('Diseño',self)
        self.op1.clicked.connect(self.Resol)
        self.op2=QPushButton('Optimizacion',self)
        self.op3=QPushButton('Reporte',self)
        self.op3.setCursor(Qt.PointingHandCursor)
        self.op3.clicked.connect(self.PDFGen)
        self.op1.setGeometry(10,130,230,30)
        self.op2.setGeometry(10,165,230,30)
        self.op3.setGeometry(10,200,230,30)
        self.op1.clicked.connect(self.Resol)
        self.op2.clicked.connect(self.show_dialog)
        self.autor=QLabel('By Oscar Marquez',self)
        self.autor.setGeometry(870,520,150,20)
        self.MSup=QFrame(self)
        self.MSup.setGeometry(0,0,1000,50)
        self.MSup.setStyleSheet('background-color:rgb(185, 225, 255)')
        self.cerrar=QPushButton('X',self)
        self.cerrar.setGeometry(960,13,30,30)
        self.cerrar.setStyleSheet('QPushButton::hover''{''background-color: #ff5a97''}')
        self.cerrar.setCursor(Qt.PointingHandCursor) #Para poner el punto como una mano
        self.cerrar.clicked.connect(self.Cerrar)


    def valor(self):
        #print(self.Confiabilidad.currentText())
        #print(self.NCapa.currentIndex())
        i=self.Confiabilidad.currentIndex()
        ZrValue=[0,-0.253,-0.524,-0.674,-0.841,-1.037,-1.282,-1.340,-1.405,-1.476,-1.555,-1.645,-1.751,-1.881,-2.054,-2.327]
        self.ZrA.setText(str(ZrValue[i]))
        self.SN1.setText('')
        self.SN2.setText('')
        self.SN3.setText('')
        self.e1.setText('')
        self.e2.setText('')
        self.e3.setText('')


    def Formulario(self):
        #posicion
        x,y=280,65
        estilo='background-color: white; border: 1px solid rgb(200,200,200);text-align:right'
        St_LM='background-color: rgb(255,255,255);'
        St_CM='border-radius: 10px;background-color: rgb(255,255,255);'
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(1)
        self.shadow.setYOffset(1)
        self.shadow1 = QGraphicsDropShadowEffect()
        self.shadow1.setBlurRadius(20)
        self.shadow1.setXOffset(1)
        self.shadow1.setYOffset(1)
        self.fram1 = QFrame(self)
        self.fram2 = QFrame(self)
        self.fram1.setGeometry(0,50,250,600)
        self.fram2.setGeometry(x,y,410,220)
        self.fram1.setStyleSheet(St_LM)
        self.fram2.setStyleSheet(St_CM)
        self.frame3=QFrame(self)
        self.frame3.setGeometry(250,513,750,35)
        self.frame3.setStyleSheet(St_LM)
        self.titl=QLabel('Parametros de diseño',self)
        self.titl.setGeometry(x+25,y+5,180,30)
        self.titl.setStyleSheet('color:rgb(63, 65, 77);font-size: 15px;font-weight: bold;')
        self.fram1.setGraphicsEffect(self.shadow)
        self.fram2.setGraphicsEffect(self.shadow1)
        self.Confiabilidad=QComboBox(self)
        self.Confiabilidad.setGeometry(x+250,y+55,120,25)
        self.Confiabilidad.addItems(['50','60','70','75','80','85','90','91','92','93','94','95','96','97','98','99'])
        self.Confiabilidad.currentIndexChanged.connect(self.valor)
        self.Confiabilidad.setCursor(Qt.PointingHandCursor)
        self.ZrA=QLineEdit(self)
        self.SoA=QLineEdit(self)
        self.PSIA=QLineEdit(self)
        self.W18A=QLineEdit(self)
        #Ejecuta la funcion una vez termine de modificar
        self.ZrA.selectionChanged.connect(self.Borrar)
        self.SoA.selectionChanged.connect(self.Borrar)
        self.PSIA.selectionChanged.connect(self.Borrar)
        self.W18A.selectionChanged.connect(self.Borrar)
        #Remplazar texto inicial
        self.ZrA.setText('0.00')
        self.SoA.setText('0.45')
        self.PSIA.setText('1.70')
        self.W18A.setText('8000000')
        self.ZrA.setValidator(QtGui.QDoubleValidator())
        self.SoA.setValidator(QtGui.QDoubleValidator())
        self.PSIA.setValidator(QtGui.QDoubleValidator())
        self.W18A.setValidator(QtGui.QDoubleValidator())
        self.ZrA.setAlignment(Qt.AlignRight)
        self.SoA.setAlignment(Qt.AlignRight)
        self.PSIA.setAlignment(Qt.AlignRight)
        self.W18A.setAlignment(Qt.AlignRight)
        self.item1=QLabel('Confiabilidad (R) ',self).setGeometry(x+35,y+50,180,30)
        self.item1=QLabel('Desviación estándar normal (Zr):',self).setGeometry(x+35,y+80,180,30)
        self.item1=QLabel('Error estándar (So):',self).setGeometry(x+35,y+110,180,30)
        self.item1=QLabel('Diferencia índice de servicio (DPSI):',self).setGeometry(x+35,y+140,180,30)
        self.item1=QLabel('Ejes equivalentes (N):',self).setGeometry(x+35,y+170,180,30)
        self.ZrA.setGeometry(x+250,y+85,120,25)
        self.SoA.setGeometry(x+250,y+115,120,25)
        self.PSIA.setGeometry(x+250,y+145,120,25)
        self.W18A.setGeometry(x+250,y+175,120,25)
        #self.WA.setGeometry(x+250,y+240,120,25)
        #self.WA.setReadOnly(True)

    def BarraInf(self):
        x,y = 280,300
        St_CM='border-radius: 10px;background-color: rgb(255,255,255);'
        self.shadow1 = QGraphicsDropShadowEffect()
        self.shadow1.setBlurRadius(20)
        self.shadow1.setXOffset(1)
        self.shadow1.setYOffset(1)
        self.fram5 = QFrame(self)
        self.fram5.setGeometry(x,y,690,195)
        self.fram5.setStyleSheet(St_CM)
        self.fram5.setGraphicsEffect(self.shadow1)
        self.titl=QLabel('Carpeta asfaltica',self)
        self.titl.setGeometry(x+25,y+5,180,30)
        self.titl.setStyleSheet('color:rgb(63, 65, 77);font-size: 12px;font-weight: bold;')
        self.titl=QLabel('Base gralunar',self)
        self.titl.setGeometry(x+300,y+5,180,30)
        self.titl.setStyleSheet('color:rgb(63, 65, 77);font-size: 12px;font-weight: bold;')
        self.titl=QLabel('Sub-Base',self)
        self.titl.setGeometry(x+550,y+5,180,30)
        self.titl.setStyleSheet('color:rgb(63, 65, 77);font-size: 12px;font-weight: bold;')
        #Input carpeta asfaltica
        self.titl=QLabel('a1:',self).setGeometry(x+25,y+45,180,30)
        self.a1=QLineEdit(self)
        self.a1.setGeometry(x+55,y+50,120,25)
        self.a1.setAlignment(Qt.AlignRight)
        self.a1.setValidator(QtGui.QDoubleValidator())
        self.a1.setText('0.488')
        self.a1.selectionChanged.connect(self.Borrar)
        self.titl=QLabel('Subrasante:',self).setGeometry(x+25,y+80,180,30)
        self.titl=QLabel('Mr:',self).setGeometry(x+25,y+110,180,30)
        self.Mr3=QLineEdit(self)
        self.Mr3.setGeometry(x+55,y+115,120,25)
        self.Mr3.setAlignment(Qt.AlignRight)
        self.Mr3.setValidator(QtGui.QDoubleValidator())
        self.Mr3.setText('10500')
        self.Mr3.selectionChanged.connect(self.Borrar)
        self.titl=QLabel('SN3',self)
        self.titl.setGeometry(x+25,y+140,180,30)
        self.SN3=QLineEdit(self)
        self.SN3.setGeometry(x+55,y+145,120,25)
        self.SN3.setReadOnly(True)
        self.SN3.setAlignment(Qt.AlignRight)
        self.SN3.setValidator(QtGui.QDoubleValidator())
        #imput base granular
        self.titl=QLabel('Mr:',self).setGeometry(x+270,y+45,180,30)
        self.Mr1=QLineEdit(self)
        self.Mr1.setText('30000')
        self.Mr1.setGeometry(x+300,y+50,120,25)
        self.Mr1.setAlignment(Qt.AlignRight)
        self.Mr1.setValidator(QtGui.QDoubleValidator())
        self.Mr1.selectionChanged.connect(self.Borrar)
        self.titl=QLabel('a2:',self).setGeometry(x+270,y+75,180,30)
        self.a2=QLineEdit(self)
        self.a2.setGeometry(x+300,y+80,120,25)
        self.a2.setAlignment(Qt.AlignRight)
        self.a2.setValidator(QtGui.QDoubleValidator())
        self.a2.setText('0.138')
        self.a2.selectionChanged.connect(self.Borrar)
        self.titl=QLabel('m2:',self).setGeometry(x+270,y+105,180,30)
        self.m2=QLineEdit(self)
        self.m2.setGeometry(x+300,y+110,120,25)
        self.m2.setAlignment(Qt.AlignRight)
        self.m2.setValidator(QtGui.QDoubleValidator())
        self.m2.setText('0.80')
        self.m2.selectionChanged.connect(self.Borrar)
        self.titl=QLabel('SN1:',self).setGeometry(x+270,y+135,180,30)
        self.SN1=QLineEdit(self)
        self.SN1.setGeometry(x+300,y+140,120,25)
        self.SN1.setAlignment(Qt.AlignRight)
        self.SN1.setValidator(QtGui.QDoubleValidator())
        self.SN1.setReadOnly(True)
        #input subbase
        self.titl=QLabel('Mr:',self).setGeometry(x+505,y+45,180,30)
        self.Mr2=QLineEdit(self)
        self.Mr2.setGeometry(x+530,y+50,120,25)
        self.Mr2.setAlignment(Qt.AlignRight)
        self.Mr2.setValidator(QtGui.QDoubleValidator())
        self.Mr2.setText('17000')
        self.Mr2.selectionChanged.connect(self.Borrar)
        self.titl=QLabel('a3:',self).setGeometry(x+505,y+75,180,30)
        self.a3=QLineEdit(self)
        self.a3.setGeometry(x+530,y+80,120,25)
        self.a3.setAlignment(Qt.AlignRight)
        self.a3.setValidator(QtGui.QDoubleValidator())
        self.a3.setText('0.120')
        self.a3.selectionChanged.connect(self.Borrar)
        self.titl=QLabel('m3:',self).setGeometry(x+505,y+105,180,30)
        self.m3=QLineEdit(self)
        self.m3.setGeometry(x+530,y+110,120,25)
        self.m3.setAlignment(Qt.AlignRight)
        self.m3.setValidator(QtGui.QDoubleValidator())
        self.m3.setText('0.80')
        self.m3.selectionChanged.connect(self.Borrar)
        self.titl=QLabel('SN2',self)
        self.titl.setGeometry(x+505,y+135,180,30)
        self.SN2=QLineEdit(self)
        self.SN2.setGeometry(x+530,y+140,120,25)
        self.SN2.setReadOnly(True)
        self.SN2.setAlignment(Qt.AlignRight)
        self.SN2.setValidator(QtGui.QDoubleValidator())

    def Borrar(self):
        self.SN1.setText('')
        self.SN2.setText('')
        self.SN3.setText('')
        self.e1.setText('')
        self.e2.setText('')
        self.e3.setText('')

    def Resultado(self):
        x,y = 705,65
        St_CM='border-radius: 10px;background-color: rgb(255,255,255);'
        self.shadow1 = QGraphicsDropShadowEffect()
        self.shadow1.setBlurRadius(20)
        self.shadow1.setXOffset(1)
        self.shadow1.setYOffset(1)
        self.fram5 = QFrame(self)
        self.fram5.setGeometry(x,y,270,220)
        self.fram5.setStyleSheet(St_CM)
        self.fram5.setGraphicsEffect(self.shadow1)
        self.titl=QLabel('Estructura de pavimento',self)
        self.titl.setGeometry(x+25,y+5,180,30)
        self.titl.setStyleSheet('color:rgb(63, 65, 77);font-size: 14px;font-weight: bold;')
        #Agregar numero de capas
        self.NCapa=QComboBox(self)
        self.NCapa.setGeometry(530,90,120,25)
        self.NCapa.addItems(['3','2','1']) #-------------------------------------------------------------------------------
        self.NCapa.currentIndexChanged.connect(self.ModCapas)
    def ModCapas(self):
        x,y = 705,65
        i=self.NCapa.currentIndex()
        if i==2:
            self.Carpeta.setGeometry(x+30,y+50,100,145)
            self.BG.setGeometry(x+30,y+85,100,0)
            self.SBG.setGeometry(x+30,y+135,100,0)
            self.a2.setText("")
            self.a2.setReadOnly(True)
            self.a3.setText("")
            self.a3.setReadOnly(True)
            self.m3.setText("")
            self.m3.setReadOnly(True)
            self.m2.setText("")
            self.m2.setReadOnly(True)
            self.Mr1.setText("")
            self.Mr1.setReadOnly(True)
            self.Mr2.setText("")
            self.Mr2.setReadOnly(True)
            self.e1.setText("CA=?")
            self.e2.setText("")
            self.e3.setText("")
            self.e1.setGeometry(x+150,y+100,180,30)
        if i==1:
            self.Carpeta.setGeometry(x+30,y+50,100,35)
            self.BG.setGeometry(x+30,y+85,100,110)
            self.SBG.setGeometry(x+30,y+135,100,0)
            self.a2.setText("")
            self.a2.setReadOnly(False)
            self.a3.setText("")
            self.a3.setReadOnly(True)
            self.m3.setText("")
            self.m3.setReadOnly(True)
            self.m2.setText("")
            self.m2.setReadOnly(False)
            self.Mr1.setText("")
            self.Mr1.setReadOnly(False)
            self.Mr2.setText("")
            self.Mr2.setReadOnly(True)
            self.e1.setText("CA=?")
            self.e2.setText("BG=?")
            self.e3.setText("")
            self.e1.setGeometry(x+150,y+50,180,30)
            self.e2.setGeometry(x+150,y+120,180,30)
        if i==0:
            self.Carpeta.setGeometry(x+30,y+50,100,35)
            self.BG.setGeometry(x+30,y+85,100,50)
            self.SBG.setGeometry(x+30,y+135,100,60)
            self.a2.setText("")
            self.a2.setReadOnly(False)
            self.a3.setText("")
            self.a3.setReadOnly(False)
            self.m3.setText("")
            self.m3.setReadOnly(False)
            self.m2.setText("")
            self.m2.setReadOnly(False)
            self.Mr1.setText("")
            self.Mr1.setReadOnly(False)
            self.Mr2.setText("")
            self.Mr2.setReadOnly(False)
            self.e1.setText("CA=?")
            self.e2.setText("BG=?")
            self.e3.setText("SBG")
            self.e1.setGeometry(x+150,y+50,180,30)
            self.e2.setGeometry(x+150,y+95,180,30)
            self.e3.setGeometry(x+150,y+150,180,30)
    def Capas(self):
        x,y = 705,65
        #Capas
        self.Carpeta=QFrame(self)
        self.Carpeta.setGeometry(x+30,y+50,100,35)
        self.Carpeta.setStyleSheet('background-color: rgb(65,59,59)')
        self.e1=QLabel('CA=?',self)
        self.e1.setGeometry(x+150,y+50,180,30)
        self.BG=QFrame(self)
        self.BG.setGeometry(x+30,y+85,100,50)
        self.BG.setStyleSheet('background-color: rgb(149,141,126)')
        self.e2=QLabel('BG=?',self)
        self.e2.setGeometry(x+150,y+95,180,30)
        self.SBG=QFrame(self)
        self.SBG.setGeometry(x+30,y+135,100,60)
        self.SBG.setStyleSheet('background-color: rgb(100,75,61)')
        self.e3=QLabel('SBG=?',self)
        self.e3.setGeometry(x+150,y+150,180,30)




    def Resol(self):
        k=self.NCapa.currentIndex() #Indica el numero de capas con las que se va a diseñar el pavimento
        if k==2:
            MR_Base=1000
            MR_SubBase=1000
            MR_Subr=float(self.Mr3.text())
        if k==1:
            MR_Base=float(self.Mr1.text())
            MR_SubBase=1000
            MR_Subr=float(self.Mr3.text())
        if k==0:
            MR_Base=float(self.Mr1.text())
            MR_SubBase=float(self.Mr2.text())
            MR_Subr=float(self.Mr3.text())
        Zr=float(self.ZrA.text())
        So=float(self.SoA.text())
        PSI=float(self.PSIA.text())
        W18=float(self.W18A.text())
        MR=[MR_Base,MR_SubBase,MR_Subr]
        j=0
        SNT=[]
        while (j<3):
            def A93(SN):
                r=Zr*So+9.36*math.log10(SN+1)-0.2+((math.log10(PSI/(4.2-1.5)))/(0.40+1094/((SN+1)**5.19)))+2.32*math.log10(MR[j])-8.07-math.log10(W18)
                return r
            i=0
            S1=0
            S2=50
            while(i<1000):
                SNi=S1+0.5*(S2-S1)
                x1,x2=A93(S1),A93(SNi)
                if x1*x2<0:
                    S1=S1
                    S2=SNi
                else:
                    S1=SNi
                    S2=S2
                i=i+1
            SNT.append(S1)
            j=j+1

        def Redondea(D):
            Nu=math.ceil(D*2.54)
            Dn=Nu/2.54
            return Dn
        def MinEst(W18):
            N=W18
            if N<150000:
                D1,D2,D3=2,4,4
            if N>=150000 and N<500000:
                D1,D2,D3=2.5,4,4
            if N>=500000 and N<2000000:
                D1,D2,D3=3,6,6
            if N>=2000000 and N<7000000:
                D1,D2,D3=3.5,6,6
            if N>=7000000:
                D1,D2,D3=4.0,6,6
            Dmin=[D1,D2,D3]
            return Dmin
        def DisCA(SN,a1,W18):
            D1=Redondea(SN/a1)
            D1m=MinEst(W18)
            D1min=D1m[0]
            D1=max(D1,D1min)
            d1=D1*2.54
            SN1_1=D1*a1
            return D1,SN1_1,d1
        def DisBA(SN1_1,SN,a,m,W18):
            D2=(SN-SN1_1)/(a*m)
            D2=Redondea(D2)
            D2m=MinEst(W18)
            D2min=D2m[1]
            D2=max(D2,D2min)
            d2=D2*2.54
            SN2_2=D2*a*m+SN1_1
            return D2,SN2_2,d2
        #Calculo de espesor de pavimento

        if k==0:
            a1=float(self.a1.text())
            a2=float(self.a2.text())
            a3=float(self.a3.text())
            m2=float(self.m2.text())
            m3=float(self.m3.text())
            self.SN1.setText(str(round(SNT[0],3)))
            self.SN2.setText(str(round(SNT[1],3)))
            self.SN3.setText(str(round(SNT[2],3)))
            CA=DisCA(SNT[0],a1,W18)
            BG=DisBA(CA[1],SNT[1],a2,m2,W18)
            SBG=DisBA(BG[1],SNT[2],a3,m3,W18)
            d1=round(CA[2])
            d2=round(BG[2])
            d3=round(SBG[2])
            self.e1.setText('CA='+str(d1)+' cm')
            self.e2.setText('BG='+str(d2)+' cm')
            self.e3.setText('SBG='+str(d3)+' cm')
        if k==1:
            a1=float(self.a1.text())
            a2=float(self.a2.text())
            m2=float(self.m2.text())
            self.SN1.setText(str(round(SNT[0],3)))
            self.SN2.setText('')
            self.SN3.setText(str(round(SNT[2],3)))
            CA=DisCA(SNT[0],a1,W18)
            BG=DisBA(CA[1],SNT[2],a2,m2,W18)
            d1=round(CA[2])
            d2=round(BG[2])
            self.e1.setText('CA='+str(d1)+' cm')
            self.e2.setText('BG='+str(d2)+' cm')
            self.e3.setText('')
        if k==2:
            a1=float(self.a1.text())
            self.SN1.setText('')
            self.SN2.setText('')
            self.SN3.setText(str(round(SNT[2],3)))
            CA=DisCA(SNT[2],a1,W18)
            d1=round(CA[2])
            self.e1.setText('CA='+str(d1)+' cm')
            self.e2.setText('')
            self.e3.setText('')


stl = """QPushButton:hover {
    background-color: rgb(68, 154, 217);
    border: None;
}
QPushButton {
    background-color: rgb(80, 181, 255);
    color:white;
    border: None;
}
QComboBox {
    background-color: rgb(220, 240, 255);
    border-radius: 5px;
    padding-left: 20px;
    min-width: 6em;
    color: black;
}
QLineEdit{
    background-color: rgb(220, 240, 255);
    border-radius:5px;
    padding: 5px;
    color:rgb(63, 65, 77);
}
QLineEdit:focus{
    background-color: rgb(185, 225, 255);
    border:1px solid rgb(170,170,170);
}

QLabel{
    color: rgb(63, 65, 77);
    font-size: 11px;
}
QPushButton#cerrar {
    font-size: 30px;
    color: #A0184B;
}
"""
app = QApplication([])
QApplication.instance().setStyleSheet(stl)
window = MainApp()
window.show()
app.exec_()
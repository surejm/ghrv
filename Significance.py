# -*- coding:utf-8 -*-


#   ----------------------------------------------------------------------
#   gHRV: a graphical application for Heart Rate Variability analysis
#   Copyright (C) 2013  Milegroup - Dpt. Informatics
#      University of Vigo - Spain
#      www.milegroup.net
#
#   Authors:
#     - Leandro Rodríguez-Liñares
#     - Arturo Méndez
#     - María José Lado
#     - Xosé Antón Vila
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#   ----------------------------------------------------------------------

import wx

from configvalues import *
import matplotlib
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import numpy as np
import os
from sys import platform



class SignificanceWindow(wx.Frame):
    """Window for significance analysis"""

    sbSignifText="  Keys: 'i'/'m' increase/lower no. of bins, '0' resets, 's' saves plot"

    def __init__(self,parent,id,title,dm):
        wx.Frame.__init__(self, parent, -1, title, size=signifWindowSize)
        
        if platform != "darwin":
            icon = wx.Icon("LogoIcon.ico", wx.BITMAP_TYPE_ICO)
            self.SetIcon(icon)

        self.signifNumBins=signifNumBins
        self.dm = dm
        
        self.Bind(wx.EVT_CLOSE,self.OnEnd)  
        
        self.WindowParent=parent
        sizer=wx.BoxSizer(wx.VERTICAL)

        panel = wx.Panel(self)

        # -------------- Begin of parameter selector

        sbParam = wx.StaticBox(panel, label="Parameter")
        sbParamSizer = wx.StaticBoxSizer(sbParam, wx.VERTICAL)
        sbParamSizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sbParamSizer2 = wx.BoxSizer(wx.HORIZONTAL)
        
        AllBandsOrig = self.dm.GetVisibleBands()[0]
        AllBands=list(AllBandsOrig)
        AllBands.remove("Heart rate")

        bandsRB=[]

        for band in AllBands:
            if len(bandsRB)==0:
                tmp = wx.RadioButton(panel, label=band, style=wx.RB_GROUP)
                tmp.SetValue(True)
            else:
                tmp = wx.RadioButton(panel, label=band)
            bandsRB.append(tmp)
            if len(bandsRB)<=6:
                sbParamSizer1.Add(tmp, wx.EXPAND) 
            else:      
                sbParamSizer2.Add(tmp, wx.EXPAND) 
        
        sbParamSizer.Add(sbParamSizer1,flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT,border=borderBig)
        sbParamSizer.Add(sbParamSizer2,flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT,border=borderBig)
        sizer.Add(sbParamSizer,flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT,border=borderBig)

        for eachRB in bandsRB:
            self.Bind(wx.EVT_RADIOBUTTON,self.OnParam,eachRB)

        self.ActiveParam = AllBands[0]

        # -------------- End of parameter selector



        # -------------- Begin of tags selector

        sbTags = wx.StaticBox(panel, label="Episodes")
        sbTagsSizer = wx.StaticBoxSizer(sbTags, wx.HORIZONTAL)

        # tagsRB = []
        self.AllTags = self.dm.GetVisibleEpisodes()[0]
        self.ActiveTagLeft = self.AllTags[0]
        self.ActiveTagRight = None
        self.dm.SetSignifPlotParams(self.ActiveTagLeft,self.ActiveTagRight,self.ActiveParam)
        
        self.cbComboLeft=wx.ComboBox(panel,
            choices=self.AllTags,
            value=self.ActiveTagLeft,
            style=wx.CB_DROPDOWN|wx.CB_READONLY
            )
        sbTagsSizer.Add(self.cbComboLeft,flag=wx.ALL | wx.EXPAND, border=borderSmall)
        self.Bind(wx.EVT_COMBOBOX, self.OnComboLeft, id=self.cbComboLeft.GetId())
        

        sbTagsSizer.AddStretchSpacer(prop=1)

        ChoicesRight = ["Outside "+self.ActiveTagLeft]+self.AllTags
        ChoicesRight.remove(self.ActiveTagLeft)

        self.cbComboRight=wx.ComboBox(panel,
            choices=ChoicesRight, 
            value="Outside "+self.ActiveTagLeft, 
            style=wx.CB_DROPDOWN|wx.CB_READONLY
            )
        sbTagsSizer.Add(self.cbComboRight,flag=wx.ALL | wx.EXPAND, border=borderSmall)
        self.Bind(wx.EVT_COMBOBOX, self.OnComboRight, id=self.cbComboRight.GetId())


        sizer.Add(sbTagsSizer,flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT,border=borderBig)

        # -------------- End of tags selector


        # -------------- Begin of figure
        if ColoredBGPlots:
            self.fig = matplotlib.figure.Figure((5.0, 4.0),facecolor=SignifBGColor)
        else:
            self.fig = matplotlib.figure.Figure((5.0, 4.0))
            
        self.fig.subplots_adjust(left=0.05, bottom=0.18, right=0.98, top=0.92, wspace=0.20, hspace=0.15)
        self.canvas = FigureCanvas(panel, -1, self.fig)
        
        self.axes = self.fig.add_subplot(111)

        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)

        # -------------- End of figure

        # -------------- Begin of textbox and buttons

        hbox = wx.BoxSizer(wx.HORIZONTAL)   


        self.textOutput = wx.TextCtrl(panel, id, 'Information', size=(400, 75), style=wx.TE_READONLY|wx.TE_MULTILINE|wx.TE_RICH2)
        self.textOutput.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL));
        hbox.Add(self.textOutput, 1, wx.LEFT | wx.TOP | wx.GROW)

        endButton = wx.Button(panel, -1, "Close", size=buttonSizeSignif)
        self.Bind(wx.EVT_BUTTON, self.OnEnd, id=endButton.GetId())
        endButton.SetToolTip(wx.ToolTip("Click to close window"))
        hbox.Add(endButton, 0, border=borderBig, flag=wx.LEFT|wx.ALIGN_BOTTOM)
                
        sizer.Add(hbox, 0, flag=wx.EXPAND|wx.ALL, border=borderBig)

        # -------------- End of textbox and buttons

        panel.SetSizer(sizer)

        self.SetMinSize(signifWindowMinSize)

#        self.sb = self.CreateStatusBar()
#        self.sb.SetStatusText(self.sbSignifText)

#        self.canvas.Bind(wx.EVT_KEY_DOWN, self.OnKeyPress)

        self.Show(True)
        self.Layout()
        self.Refresh()



    def ErrorWindow(self,messageStr,captionStr="ERROR"):
        """Generic error window"""
        dial = wx.MessageDialog(self, caption=captionStr, message=messageStr, style=wx.OK | wx.ICON_ERROR)
        result = dial.ShowModal()
        dial.Destroy()
        self.canvas.SetFocus()

    def OnEnd(self,event):
        self.WindowParent.OnSignifEnded()
        self.Destroy()

    def OnParam(self,event):
        (ATL,ATR,AP) = self.dm.GetSignifPlotParams()
        self.ActiveParam = event.GetEventObject().GetLabel()
        self.dm.SetSignifPlotParams(ATL,ATR,self.ActiveParam)
        self.Refresh()

    def OnComboLeft(self,event):
        (ATL,ATR,AP) = self.dm.GetSignifPlotParams()
        self.ActiveTagLeft = self.cbComboLeft.GetValue()
        self.cbComboRight.Clear()
        ChoicesRight = ["Outside "+self.ActiveTagLeft]+self.AllTags
        ChoicesRight.remove(self.ActiveTagLeft)
        for item in ChoicesRight:
            self.cbComboRight.Append(item)
        self.cbComboRight.SetValue("Outside "+self.ActiveTagLeft)
        self.ActiveTagRight = None
        self.dm.SetSignifPlotParams(self.ActiveTagLeft,self.ActiveTagRight,AP)
        self.Refresh()

    def OnComboRight(self,event):
        (ATL,ATR,AP) = self.dm.GetSignifPlotParams()
        self.ActiveTagRight = self.cbComboRight.GetValue()
        if self.ActiveTagRight[0:7] == "Outside":
            self.ActiveTagRight=None
        self.dm.SetSignifPlotParams(ATL,self.ActiveTagRight,AP)
        self.Refresh()
        
        
    def Refresh(self):        
        valuesLeft,valuesRight = self.dm.CreatePlotSignifEmbedded(self.fig)
        numValuesLeft=len(valuesLeft)
        numValuesRight=len(valuesRight)

        cad = self.ActiveParam+":  "
        if self.ActiveTagRight:
            cad = cad + self.ActiveTagLeft + " vs. " + self.ActiveTagRight+"\n"
        else: 
            cad = cad + self.ActiveTagLeft + " (inside vs. outside)\n"

        cad=cad+"No. points: "
        
        if not self.ActiveTagRight:
            cad = cad + str(numValuesLeft) +" (inside), "+str(numValuesRight)+" (outside)\n"
        else:
            cad = cad + str(numValuesLeft) +" ("+self.ActiveTagLeft+"), "
            cad = cad + str(numValuesRight)+" ("+self.ActiveTagRight+")\n"
            

        if (numValuesLeft>signifNumMinValues) and (numValuesRight>signifNumMinValues):
            cad=cad+ "Mean  -  in: %.3f, out: %.3f\n" % (np.mean(valuesLeft),np.mean(valuesRight))

            pvalue = self.GetPValue(valuesLeft,valuesRight,signifAlpha)[0]
#            # print "Dev1 ",np.std(valuesleft)
#            # print "Dev2 ",np.std(valuesright)
            cad=cad+ "Welch's t-test: "
            if pvalue:
                cad=cad+ "significative differences found!!" 
            else:
                cad=cad+ "significative differences not found"
#            
        else:
            cad=cad+"Not enough data: minimum no. of points is "+str(signifNumMinValues)
#            
        self.textOutput.SetValue(cad)
        self.canvas.draw()

    def GetPValue(self,a,b,alpha):
        import scipy
        n1=len(a)
        n2=len(b)
        mean1 = np.mean(a)
        mean2 = np.mean(b)
        sem1 = scipy.stats.sem(a,ddof=1)
        sem2 = scipy.stats.sem(b,ddof=1)
        svm1 = sem1**2 * n1
        svm2 = sem2**2 * n2
        t_s_prime = (mean1 - mean2)/np.sqrt(svm1/n1+svm2/n2)
        t_alpha_df1 = scipy.stats.t.ppf(1-alpha/2, n1 - 1)
        t_alpha_df2 = scipy.stats.t.ppf(1-alpha/2, n2 - 1)
        t_alpha_prime = (t_alpha_df1 * sem1**2 + t_alpha_df2 * sem2**2) / (sem1**2 + sem2**2)
        return abs(t_s_prime) > t_alpha_prime, t_s_prime, t_alpha_prime

    def GetPValueOld(self,valuesleft,valuesright,alpha):
        from scipy.stats import ttest_ind
        pvalue=ttest_ind(valuesleft,valuesright)[1]
        return (pvalue<alpha),pvalue

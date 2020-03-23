from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
import IndoseCT_funcs
import os
import json
import numpy as np

class MainWindow(FloatLayout):
  pass

class InDoseCT(App):
  def build(self):
    return MainWindow()

if __name__ == "__main__":
  InDoseCT().run()

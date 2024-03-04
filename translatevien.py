from googletrans import Translator

translator = Translator()

def translate_vi2en(text):
    return translator.translate(text, src='vi', dest='en').text

def translate_en2vi(text):
    return translator.translate(text, src='en', dest='vi').text
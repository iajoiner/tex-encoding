import json
import re
import tex_tester
MATHDIC={'\\^':'\\hat','\\v':'\\check','\\u':'\\breve','\\`':'\\grave','\\~':'\\tilde','\\=':'\\bar','\\.':'\\dot','\\"':'\\ddot',"\\'": '\\acute'}
def individual_process(font, code, tex_string, tex_engine = 'latex'):
    math_pattern = re.compile(r'\$\S*\$')
    text_font_pattern = re.compile(r'\\text\S+{\S+}')
    math_font_pattern = re.compile(r'\$\\math\S+{\S+}\$')
    text_accent_pattern = re.compile(r'\\[`\'^~"Hrvut=.bcdk]$')
    nonmath_text_accent_pattern = re.compile(r'\\[Hrtbcdk]$')
    short_math_accent_pattern = re.compile(r'\\[`\'^~"vu=.]$')
    long_math_accent_pattern = re.compile(r'\\vec$|\\widetilde$|\\widehat$')
    math_accent_pattern = re.compile(r'\\[`\'^~"vu=.]$|\\vec$|\\widetilde$|\\widehat$')
    individual_output = {}
    preamble_list = []
    latex_package_list = []
    if math_font_pattern.search(tex_string):
        pieces = tex_string.split('{', 1)
        individual_output['font'] = pieces[0][2:]
        individual_output['value'] = pieces[1][:-2]
        individual_output['usage'] = 'm'
        if long_math_accent_pattern.search(individual_output['value']):
            individual_output['usage'] = 'ma'
    elif text_font_pattern.search(tex_string):
        pieces = tex_string.split('{', 1)
        individual_output['font'] = pieces[0][1:]
        individual_output['value'] = pieces[1][:-1]
        individual_output['usage'] = 't'
        if short_math_accent_pattern.search(individual_output['value']):
            individual_output['usage'] = 'tma'
            individual_output['mav'] = MATHDIC[individual_output['value']]
        elif nonmath_text_accent_pattern.search(individual_output['value']):
            individual_output['usage'] = 'ta'
    elif math_pattern.search(tex_string):
        individual_output['value'] = tex_string[1:-1]
        individual_output['usage'] = 'm'
        if long_math_accent_pattern.search(individual_output['value']):
            individual_output['usage'] = 'ma'
    else:
        individual_output['value'] = tex_string
        individual_output['usage'] = 't'
        if short_math_accent_pattern.search(tex_string):
            individual_output['usage'] = 'tma'
            individual_output['mav'] = MATHDIC[tex_string]
        elif nonmath_text_accent_pattern.search(tex_string):
            individual_output['usage'] = 'ta'
    #Preambles
    if font == 'cmcsc' and code >= 0 and code <= 10:#mathsc:
        preamble_list.append('\\DeclareMathAlphabet{\\mathsc}{OT1}{cmr}{m}{sc}')
    
    if font == 'cmsy' and code >= 65 and code <= 90:#mathcal
        individual_output['value'] = tex_string[-2]
        individual_output['font'] = 'mathcal'
    if latex_package_list:
        individual_output['packages'] = latex_package_list
    if preamble_list:
        individual_output['preamble'] = preamble_list
    return individual_output
#Process an array of TeX symbols related to a font
def array_process(font, array, start = 0, end = 127, tex_engine = 'latex'):    
    code_range = range(start, end + 1)
    output = {}
    for code in code_range:
        output[code] = individual_process(font, code, array[code - start], tex_engine)
    final_output = {}
    final_output['values'] = output
    if font == 'msam':#Font-wise preamble list
        final_output['preamble'] = ['amssymb']
    return final_output
#Process an array of TeX symbols related to a font
def array_process_discrete(font, array, code_array, tex_engine = 'latex'):    
    output = {}
    tex_length = len(array)
    code_length = len(code_array)
    if tex_length != code_length:
        print(f'Warning! tex_length is {tex_length} while code_length is {code_length}.')
        return {}
    for i in range(tex_length):
        output[code_array[i]] = individual_process(font, code_array[i], array[i], tex_engine)
    final_output = {}
    final_output['values'] = output
    if font == 'msbm':#Font-wise preamble list
        final_output['preamble'] = ['amssymb']
    return final_output
expanded_dict = {}
with open('/Users/CatLover/Documents/Tex/dvi2tex/symbol_db.json', 'r') as json_file:
    db_dict = json.load(json_file)
    for key in db_dict.keys():
        key_json = db_dict[key]
        if isinstance(key_json, list):
            expanded_dict[key] = array_process(key, key_json)
        elif isinstance(key_json, dict):
            expanded_dict[key] = array_process_discrete(key, key_json['values'], key_json['codes'])
    with open('/Users/CatLover/Documents/Tex/dvi2tex/expanded_symbol_db.json', 'w') as new_json_file:
        json.dump(expanded_dict, new_json_file)

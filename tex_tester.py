# tex_tester 1.0
# Author: Ying Zhou
import subprocess
import os
import re
ALL_ENGINES = ['tex','latex','pdftex','pdflatex','xetex','xelatex','luatex','lualatex']
ENGINES_USING_LATEX = ['latex','pdflatex','xelatex','lualatex']
USES_LATEX = {'tex': False,'latex': True, 'pdftex': False, 'pdflatex': True, 'xetex': False, 'xelatex': True, 'luatex': False, 'lualatex': True}
def test_default(tex_string, tex_engine = 'latex', latex_packages = []):
    if tex_engine not in USES_LATEX or not USES_LATEX[tex_engine]:
        return '\\relax ' + tex_string + '\\bye'
    else:
        package_line = ''
        for package in latex_packages:
            package_line = package_line + '\\usepackage{' + package + '}'
        return '\\documentclass{article}' + package_line + '\\begin{document}' + tex_string + '\\end{document}'
def process(tex_string, mode = 0):
    if mode == 0:#Text
        return tex_string
    elif mode == 1:#Math
        return '$' + tex_string + '$'
    elif mode == 2:#Text{}
        return tex_string + '{}'
    elif mode == 3:#Math{}
        return '$' + tex_string + '{}$'
    else:
        print(f'Unknown mode: {mode}')
        return tex_string
def run_test(tex_string, tex_engine = 'latex', latex_packages = [], test_mode = False):
    accent_pattern = re.compile(r'\\[`\'^~"Hrvut=.bcdk]$|\\vec$|\\widetilde$|\\widehat$')
    is_accent = False
    if not test_mode:
        filename = 'TEX_TESTING'
    return_codes = [False, False, False, False] #Text, Math, Text Accent, Math Accent
    if accent_pattern.search(tex_string):#Is it an accent?
        is_accent = True
    for i in range(4):
        if i >= 2 and not is_accent:
            break
        completed_tex_string = test_default(process(tex_string, i), tex_engine, latex_packages)
        if test_mode:
            filename = 'TEX_TESTING' + '_' + tex_engine + str(i) 
            with open(filename + '.tex', 'w') as f:
                f.write(completed_tex_string)
        completed_process = subprocess.run([tex_engine, "-jobname=" + filename, "-halt-on-error", "-interaction=nonstopmode", completed_tex_string], capture_output = True, text = True)
        code = completed_process.returncode
        log_string_1 = str(completed_process.stdout)
        #print('stdout\n' + log_string_1)
        log_string_2 = str(completed_process.stderr)
        #print('stderr\n' + log_string_2)
        try:
            os.remove(filename + '.aux')
        except Exception:
            pass
        if code != 0:
            return_codes[i] = False 
        else:
            if i == 1 or i == 3:#Is the command actually valid in math mode??
                if 'invalid in math mode on' in log_string_1 or 'invalid in math mode on' in log_string_2:
                    return_codes[i] = False
                else:
                    return_codes[i] = True
            else:
                return_codes[i] = True
    if not any(return_codes):
        print(f'Warning: {tex_string} is invalid using engine {tex_engine}!')
    return return_codes
def run_multiple_engine_test(tex_string, tex_engines = ALL_ENGINES, latex_packages = [], test_mode = False):
    return_codes = {}
    if latex_packages:#Any command that requires LaTeX packages must not be used on an engine without LaTeX
        for engine in tex_engines:
            if engine in ENGINES_USING_LATEX:
                return_codes[engine] = run_test(tex_string, engine, latex_packages, test_mode)
            else:
                return_codes[engine] = [False, False, False, False]
    else:
        for engine in tex_engines:
            return_codes[engine] = run_test(tex_string, tex_engine = engine, test_mode = test_mode)
    return return_codes
        
#print(run_multiple_engine_test('\\big\/', test_mode = False))
#print(run_test(test_multipl('\\ell', )))

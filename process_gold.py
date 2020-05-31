import os
import glob
import re
from lxml import etree
import tags
import conj


def format_text(s):
    nt_tr = '.,:\-'
    tr = '?!;()[\]'
    br = '()[\]'
    qu = '\'\"«»„““”‘’'

    # Однозначно терминальные ЗП: вопросительный и восклицательный знаки, точка с запятой и скобки
    s = re.sub(r' {4}([%s]?[%s]+[%s]?)(?=[\n\r])' % (qu, tr, qu),
               '    <pc ana="PM,Tr,_">\\1</pc>', s)

    # Единственный однозначно нетерминальный ЗП - кавычка
    s = re.sub(r' {4}([%s]+)(?=[\n\r])' % qu,
               '    <pc ana="PM,Nt,_">\\1</pc>', s)

    # Неоднозначные ЗП: точка, запятая, двоеточие, тире
    s = re.sub(r' {4}([%s%s%s]*[%s]+[%s]*[%s]?)(?=[\n\r])' % (qu, nt_tr, tr, nt_tr, br, qu),
               '    <pc ana="PM,Nt,Tr">\\1</pc>', s)

    # Сокращения
    s = re.sub(r' {4}((в|вв|г|др|км|млн|млрд|пр|тыс)\.?)(?=[\n\r])',
               '    <w lex="\\1" gr="S,inan,|gender,|case,|number">\\1</w>', s)
    s = re.sub(r' {4}(у\. ?е\.)(?=[\n\r])',
               '    <w lex="\\1" gr="S,inan,|gender,|case,|number">\\1</w>', s)
    s = re.sub(r' {4}(т\. ?к\.)(?=[\n\r])',
               '    <w lex="\\1" gr="CONJ">\\1</w>', s)

    # Числа
    s = re.sub(r' {4}(\d+-\w+)(?=[\n\r])',
               '    <w lex="\\1" gr="A,|gender,|case,plen,|number">\\1</w>', s)
    s = re.sub(r' {4}(\d+)(?=[\n\r])',
               '    <w lex="\\1" gr="NM">\\1</w>', s)

    # Пункты типа а), б) и т. д.
    s = re.sub(r' {4}(\w\s*\))',
               '    <w lex="\\1" gr="NONLEX">\\1</w>', s)

    # Всё, что осталось, оформляем как glyph
    s = re.sub(r' {4}(?!<)(.+)', '    <g>\\1</g>', s)

    return s


def format_tag(ps, ts):
    # ps == p_set, ts == tags.gold_X
    for t in ps:
        if t in ts:
            return ts[t]

    return '_'


def format_parse(pt):
    # type(pt) = list из 1 элемента (списка тегов из 'gr' через запятую)
    ana = []
    # массив для новых тегов

    for parse in pt:
        # type(p_set) == list of tags(str)
        # parse = (str) теги через запятую
        p_set = parse.split(',')
        # p_set = (list) тегов в формате (str)
        pos = format_tag(p_set, tags.gold_pos)

        # теги в новом формате:
        animacy = format_tag(p_set, tags.gold_animacy)
        case = format_tag(p_set, tags.gold_case)
        number = format_tag(p_set, tags.gold_number)
        gender = format_tag(p_set, tags.gold_gender)
        person = format_tag(p_set, tags.gold_person)
        aspect = format_tag(p_set, tags.gold_aspect)

        if pos in ('Nn', 'Pn'):
            # исправлена одушевленность
            animacy = '_'

            if number == 'Pl':
                gender = '_'

        elif pos == 'Vb':

            if 'inf' in p_set:
                pos = 'If'
            elif 'partcp' in p_set:
                if 'plen' in p_set:
                    pos = 'Pt'
                else:
                    pos = 'Vp'
            elif 'ger' in p_set:
                pos = 'Dp'

            if person == '_' and number == 'Pl':
                gender = '_'

        elif pos == 'Aj':

            if 'brev' in p_set:
                pos = 'Ap'

            if number == 'Pl':
                gender = '_'          

        elif pos == 'Nu':

            if 'comp' in p_set:
                pos = 'Cm'

        ana += [','.join((pos, animacy, case, number, gender, person, aspect))]

    return ';'.join(ana)


def process(inpt_dir, otpt_dir):
    os.makedirs(otpt_dir, exist_ok=True)
    os.chdir(inpt_dir)
    print('Please wait. Python is processing your data...')
    files = glob.glob('*.xml')

    # Словарь для статистики
    trg_dct = {}

    for file in files:
        inpt = open(file, mode='r', encoding='utf-8')
        text = format_text(inpt.read())

        parser = etree.XMLParser(huge_tree=True)
        root = etree.fromstring(text, parser)
        # type(root) = Element - что-то среднее между dict и list
        otpt_tree = etree.Element('text')
        glyph_log = ''

        for i, par in enumerate(root):
            p = etree.SubElement(otpt_tree, 'p')
            # example -> SubElement(parent, tag, attrib={}, **extra)
            p.set('n', str(i + 1))
            # Element.set(key,value) == ("n", element number in root)
            # разбивает файл на кусочки открывающим тегом <p n='number'> 

            for j, node in enumerate(par):
                try:
                    next_node = par[j + 1].get('lex')
                    next_ana = par[j + 1].get('gr')
                    next_pair = '%s %s' % (par[j + 1].get('lex'), par[j + 2].get('lex'))

                    if node.tag == 'pc':
                        # <pc> == знак препинания
                        pc = etree.SubElement(p, 'pc')
                        pc.text = node.text

                        # Если следующий узел - союз из списка Арины, то это терминал
                        if next_node in conj.sing or next_pair in conj.doub:
                            pc.set('ana', 'PM,Tr,_')
                        # If all else fails, признаём неоднозначность
                        else:
                            pc.set('ana', node.get('ana'))

                        trg_dct.setdefault(pc.get('ana'), 0)
                        trg_dct[pc.get('ana')] += 1

                # Если возбуждается исключение, то мы дошли до (пред)последнего узла
                # Если это знак препинания, то это определённо терминал
                except IndexError:
                    if node.tag == 'pc':
                        pc = etree.SubElement(p, 'pc')
                        pc.text = node.text
                        pc.set('ana', 'PM,Tr,_')

                        trg_dct.setdefault(pc.get('ana'), 0)
                        trg_dct[pc.get('ana')] += 1

                finally:
                    if node.tag == 'w':
                        w = etree.SubElement(p, 'w')
                        try:
                            ana = format_parse(node.get('gr').split(';'))
                            # split(';') - чтобы из строки с тегами сделать список из 1 элемента
                            # этот один элемент - список тегов через запятую
                        except AttributeError:
                            ana = 'Zr'
                        
                        w.text = node.text
                        w.set('lemma', node.get('lex'))
                        w.set('ana', ana)

                        # приписывание предлогам падежа, с которым они употреблены
                        # (его "просачивание" от рядом стоящего слова)
                        if w.get('ana') == ("Pp,_,_,_,_,_,_"):
                            try: 
                                next_ana_list = next_ana.split(',')
                                x = 0
                                while (x < len(next_ana_list)-1):
                                    case_next = format_tag([next_ana_list[x]], tags.gold_case)
                                    if case_next != '_':
                                        w.set('ana', "Pp,_,%s,_,_,_,_" % case_next)
                                       # print(case_next)
                                    x = x +1
                            except AttributeError:
                                y = 0                            
                            
                        trg_dct.setdefault(w.get('ana'), 0)
                        trg_dct[w.get('ana')] += 1

                    elif node.tag == 'g':
                        g = etree.SubElement(p, 'g')
                        g.text = node.text

                        # Висячие символы попутно фиксируем
                        # \t - горизонтальная табуляция
                        glyph_log += '%d\t%s\n' % (i + 1, g.text)

        os.chdir(otpt_dir)

        with open(file, mode='w', encoding='utf-8') as otpt:
            xml = etree.tostring(otpt_tree, method='xml', encoding='utf-8', xml_declaration=True, pretty_print=True)
            otpt.write(xml.decode())

        with open(file[:-4] + '_glyph_log.txt', mode='w', encoding='utf-8') as log:
            log.write(glyph_log)

        with open('trg_log.txt', mode='w', encoding='utf-8') as trg_log:
            for pair in sorted(trg_dct.items(), key=lambda x: -x[1]):
                trg_log.write('%s\t%d\n' % pair)

        os.chdir(inpt_dir)
        inpt.close()


if __name__ == '__main__':
    try:
        process(os.getcwd() + '\\gold', os.getcwd() + '\\otpt')
    except FileNotFoundError:
        print('Error: source file missing.')

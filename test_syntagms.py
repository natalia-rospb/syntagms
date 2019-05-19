import pymorphy2
import nltk 
import re
import string
import process_inpt
import csv
import time
import prep

morph = pymorphy2.MorphAnalyzer()

class Profiler(object):
    """
    Shows how long does it take for this program to work.
    """
    def __enter__(self):
        self._startTime = time.time()

    def __exit__(self, type, value, traceback):
        print("Elapsed time: {:.3f} sec".format(time.time() - self._startTime))
 
def csv_reader(file_obj, number_of_strings):
    """
    Reads the necessary number of strings from a csv file
    @param file_obj: csv file to read
    @param number_of_strings: type = int
    """
    reader = csv.reader(file_obj)
    csv_list = []
    for i, row in enumerate(reader):
        if i >= number_of_strings:
            break
        csv_list.append(" ".join(row))
    return csv_list

def text_substitution(line,subStrOld,subStrNew):
    """
    Is used to substitute <header> and </header> tags by a terminal punctuation mark
    to indicate the beginning and the end of the sentence.
    Also used to format tags after reading gold trigrams from the csv file.
    """
    lenStrOld = len(subStrOld)
    while line.find(subStrOld) >= 0:
        i = line.find(subStrOld)
        line = line[:i] + subStrNew + line[i+lenStrOld:]        
    return line

def get_gold_trigram_dict(csv_path, number_of_strings):
    """
    @param csv_path: path to the csv file with gold trigrams
    @param number_of_strings: int variable showing number of trigrams to be read
    @return gold: dict with n the most frequent trigrams from the gold standart as keys
    and their frequencies as values
    """
    with open(csv_path, "r") as f_obj:
        #max number of strings = 126419
        gold_csv = csv_reader(f_obj, number_of_strings)
        gold = {}
        gold_trigram = []
        for string in gold_csv:
            string = text_substitution(string, ' ', ',')
            tags = string.split(';')
            gold_trigram.append(tags[0])
            gold_trigram.append(tags[1])
            gold_trigram.append(tags[2])
            gold[str(gold_trigram)] = tags[3]
            gold_trigram.clear()
    return gold

def get_syntagms(text300, number_of_strings):
    gold = get_gold_trigram_dict("trigrams.csv", number_of_strings)
    text300_with_syntagm_boundaries = ''
    for i, line in enumerate(text300):
        # преобразуем теги <header> и </header> 
        line = text_substitution(line, '<header>', '')
        line = text_substitution(line, '</header>', '!')
        # Массив токенов
        line_tokens = nltk.word_tokenize(line)
        x = 0
        n = 1
        while (x < len(line_tokens)- 1):
            # создаем тройки токенов = движущееся окно
            # каждый токен проверяем на наличие в списке предлогов - если есть, нужно его размножить
            # каждый рабор токена = массив упорядоченных словарей вида {разбор: лемма}
            # X_parses = список всех разборов токена в позиции X в нужной кодировке тегов
            
            #left
            if line_tokens[x-1] in prep.prep_case:
                left_parses = []
                for case in prep.prep_case[line_tokens[x-1]]:
                    left_parses.append('Pp,_,%s,_,_,_,_' %str(case))
            else:
                left_token = process_inpt.format_parse_list([morph.parse(line_tokens[x-1])])
                left_parses = list(left_token[0].keys())
                
            #central
            if line_tokens[x] in prep.prep_case:
                central_parses = []
                for case in prep.prep_case[line_tokens[x]]:
                    central_parses.append('Pp,_,%s,_,_,_,_' %str(case))
            else:
                central_token = process_inpt.format_parse_list([morph.parse(line_tokens[x])])
                central_parses = list(central_token[0].keys())
            # выкидываем триграммы, где центр - ЗП
            if central_parses[0].startswith('PM'):
                x = x + 1
                continue
            
            #right
            if line_tokens[x+1] in prep.prep_case:
                right_parses = []
                for case in prep.prep_case[line_tokens[x+1]]:
                    right_parses.append('Pp,_,%s,_,_,_,_' %str(case))
            else:    
                right_token = process_inpt.format_parse_list([morph.parse(line_tokens[x+1])])
                right_parses = list(right_token[0].keys())
                
            # создаем триграммы, комбинаторика    
            trigram = ['0','0','0']
            trigram_cache = {}
            for left_parse in left_parses:
                del trigram[0]
                trigram.insert(0, left_parse)
                for central_parse in central_parses:
                    del trigram[1]
                    trigram.insert(1, central_parse)
                    for right_parse in right_parses:
                        del trigram[2]
                        trigram.insert(2, right_parse)
                        
                        # записываем все варианты разбора в файл - пригодится в будущем
                        file = open('all_parses_combinations.txt', 'a', encoding='utf-8-sig')
                        file.write(str(trigram) + ';\n')
                        file.close()
                        
                        # ищем триграмму каждую в списке "золотых" триграмм
                        for key in gold.keys():
                            if str(trigram) == key:
                                trigram_cache[str(trigram)] = gold[str(trigram)]
                                
            # ставим границу синтагмы, если в списке триграмм для всех разборов трех соседних токенов не нашлось
            if (len(trigram_cache.keys()) == 0):
                y = line.find(line_tokens[x] + ' ' + line_tokens[x+1])
                z = line.find(line_tokens[x] + line_tokens[x+1])
                if y > -1:
                    line = line[:y + len(line_tokens[x])] + '[%s]' %str(n) + line[y + len(line_tokens[x]):]
                    n = n+1
                if z > -1:
                    line = line[:z + len(line_tokens[x])] + '[%s]' %str(n) + line[z + len(line_tokens[x]):]
                    n = n+1
                trigram_cache.clear()
            x = x + 1
##            if (x == len(line_tokens)- 1):
##                line = line + '[%s]' %str(n)
        text300_with_syntagm_boundaries += line + '\n'
    return text300_with_syntagm_boundaries

def main(): 
    with open('300.txt') as file300:
        text300 = file300.readlines()
    #text = ['рано утром в морозном лесу стояли хорошие красные башмаки.']
    text = ['Действующему мэру Екатеринбурга Евгению Ройзману также дали слово. Он отметил, что в пояснительной записке законопроекта нет обоснования для отмены прямых выборов. «Когда говорят про экономию, то забывают, что это 150 миллионов раз в пять лет. Но на пиар губернатора тратят 500 миллионов в год», — сказал глава города. Ройзман добавил, что выборы мэра — это «единственная возможность жителей участвовать в политической жизни города», и лишать их этого несправедливо и оскорбительно по отношению к екатеринбуржцам. ']
    file = open('syntagm_result.txt', 'w', encoding='utf-8-sig')
    file.write(get_syntagms(text300, 4000))
    file.close()
            


if __name__=='__main__':
    with Profiler() as p:
        main()

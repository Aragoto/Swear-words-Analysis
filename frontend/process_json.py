# Group 66 Swear Words Analysis
# Xinshu Li 875109
# Dongting Hu 960886
# Qinwei Yuan 1006223
# Ansheng Dong  989973
# Tonghao Wang 1039694
import json
import pandas as pd
import get_dirty_view_4
import get_emotion_view_4
from importlib import reload

# filepath for AURIN data and geojson
polygon_filepath = 'static/js/VIC_LOCALITY_POLYGON_shp.json'
economic_filepath = 'static/economic_index.csv'
education_filepath = 'static/edu_level.csv'
unemployment_filepath = 'static/umploy_city.csv'
with open(polygon_filepath, "r", encoding='utf-8') as f:
    data = json.load(f)
city_list = []
city_list_2 = [line['properties']['VIC_LGA__3'] for line in data['features']]
# filter out some cities which has same name. Same name cities will cause problem in the application
for city in city_list_2:
    if city not in city_list:
        city_list.append(city)
# get a dictionary which converts city to id in geojson for further use
city_id = {line['properties']['VIC_LGA__3']: line['properties']['LG_PLY_PID'] for line in data['features']}
# get a dictionary which converts id to city for further use
id_to_name = {line['properties']['LG_PLY_PID']: line['properties']['VIC_LGA__3'] for line in data['features']}

# get raw data from views in couchdb and AURIN, reload the data every time calling this function
def get_data():
    reload(get_dirty_view_4)
    reload(get_emotion_view_4)
    economic_index = {'Yarra': 915.3701184920455,
                      'Brimbank': 1003.7812062682216,
                      'Port Phillip': 981.1578423000285,
                      'Hobsons Bay': 1001.8050326649661,
                      'Stonnington': 1022.925801471256,
                      'Maribyrnong': 945.2896029552392,
                      'Boroondara': 1043.7740574330924,
                      'Pyrenees': 979.843055736001,
                      'Greater Geelong': 1010.6213784135241,
                      'Knox': 1030.6406389195738,
                      'Bayside': 1064.7036371695867,
                      'Benalla': 934.0,
                      'Greater Bendigo': 937.9184480771246,
                      'Glen Eira': 1018.5811507788626,
                      'Casey': 1041.1828882751515,
                      'Whitehorse': 1005.613257481037,
                      'Moreland': 959.8043626007315,
                      'Manningham': 1041.1254656435585,
                      'Darebin': 967.5969777140039,
                      'Ballarat': 1016.6571127502634,
                      'Monash': 996.1380200699767,
                      'Colac Otway': 983.6374296217022,
                      'Melbourne': 854.6826737217212,
                      'Frankston': 986.626862589619,
                      'Mount Alexander': 964.0,
                      'Yarra Ranges': 1057.3479446740935,
                      'Maroondah': 1039.1821477440335,
                      'Greater Dandenong': 951.8996823413802,
                      'Nillumbik': 1070.1035937126335,
                      'Mornington Peninsula': 1031.6492899304542,
                      'Baw Baw': 988.362579025553,
                      'Campaspe': 1002.7735938989514,
                      'Banyule': 1029.97062689249,
                      'South Gippsland': 994.0,
                      'Cardinia': 1014.979043419024,
                      'Macedon Ranges': 1038.786825487623,
                      'Southern Grampians': 963.0,
                      'Wyndham': 1030.9459571170241,
                      'Mildura': 992.6704124122982,
                      'East Gippsland': 969.6698502680387,
                      'Surf Coast': 1064.86046213642,
                      'Wellington': 984.9518447408022,
                      'Melton': 993.9648897452365,
                      'Greater Shepparton': 944.2472242783124,
                      'Moira': 979.7538994800693,
                      'Glenelg': 943.0,
                      'Mitchell': 906.0,
                      'Northern Grampians': 957.0,
                      'Wangaratta': 952.0,
                      'Wodonga': 974.2801311208802}
    education_level = pd.read_csv(education_filepath)
    unemployment_rate = pd.read_csv(unemployment_filepath)
    wordcount = get_dirty_view_4.get_dirty()
    emotion = get_emotion_view_4.get_emotion()
    output = [economic_index, education_level, unemployment_rate, wordcount, emotion]
    return output

# use the raw data from all scenarios and put them into a list of dictionaries
def get_summary():
    summary = {city: {'economic_index': 0,
                      'education_level': 0,
                      'unemployment_rate': 0,
                      'word_count': 0,
                      'emotion': {'positive': 0, 'negative': 0, 'neutral': 0}} for city in city_list}
    economic_index, education_level, unemployment_rate, wordcount, emotion = get_data()
    for i, city_name in enumerate(list(economic_index.keys())):
        if city_name.upper() in summary.keys():
            summary[city_name.upper()]['economic_index'] = list(economic_index.values())[i]
    for i, city_name in enumerate(list(education_level['city'])):
        if city_name.upper() in summary.keys():
            summary[city_name.upper()]['education_level'] = float(list(education_level['year_12_ratio'])[i])
    for i, city_name in enumerate(list(unemployment_rate['city'])):
        if city_name.upper() in summary.keys():
            summary[city_name.upper()]['unemployment_rate'] = float(list(unemployment_rate['unemploy_rate'])[i])
    for i, item in enumerate(wordcount):
        city_name = item['city']
        dirty_wordcount = item['dirty_word_count']
        if city_name.upper() in summary.keys():
            summary[city_name.upper()]['word_count'] = dirty_wordcount
    for i, item in enumerate(emotion):
        city_name = item['city']
        emotion_cat = item['emotion']
        if city_name.upper() in summary.keys():
            summary[city_name.upper()]['emotion'][emotion_cat.lower()] = item['emotion_count']
    return summary

# given a scenario and data point to get the percentile of this data point in this scenario
# if the data is not in the population or the data value is 0 it will return 0
def get_percentile(scenario, data, datalist):
    def get_index(value, lst):
        index = 0
        for i in range(len(lst)):
            if value <= lst[i]:
                index = i
                break
        return index
    if scenario == 'economic':
        if data == 0:
            percentile = 0
        else:
            try:
                percentile = round((datalist.index(data) + 1) / len(datalist), 4)
            except Exception as e:
                print('Data not in the Population, return 0')
                percentile = 0
    elif scenario == 'education':
        if data == 0:
            percentile = 0
        else:
            try:
                percentile = round((datalist.index(round(data, 9)) + 1) / len(datalist), 4)
            except Exception as e:
                print('Data not in the Population, return 0')
                percentile = 0
    elif scenario == 'unemployment':
        if data == 0:
            percentile = 0
        else:
            try:
                percentile = round((datalist.index(data) + 1) / len(datalist), 4)
            except Exception as e:
                print('Data not in the Population, return 0')
                percentile = 0
    else:
        if data == 0:
            percentile = 0
        else:
            try:
                percentile = round(get_index(data, datalist)/ len(datalist), 4)
            except Exception as e:
                print('Data not in the Population, return 0')
                percentile = 0
    return percentile

# output the data city by city in list of dictionaries
def output_data():
    summary = get_summary()
    economic_index, education_level, unemployment_rate, wordcount, emotion = get_data()
    economic_sort = sorted(list(economic_index.values()))
    education_sort = sorted([round(value, 9) for value in list(education_level['year_12_ratio'])])
    unemployment_sort = sorted(list(unemployment_rate['unemploy_rate']))
    word_sort = sorted([city['dirty_word_count'] for city in wordcount])
    output = []
    count = 0
    for city in city_list:
        dic = {'LG_PLY_PID': city_id[city]}
        dic['EDUCATION'] = summary[city]['education_level']
        dic['ECONOMIC'] = summary[city]['economic_index']
        dic['UNEMPLOYMENT'] = summary[city]['unemployment_rate']
        dic['WORD_COUNT'] = summary[city]['word_count']
        dic['EDUCATION_PERCENTILE'] = get_percentile('education', summary[city]['education_level'], education_sort)
        dic['ECONOMIC_PERCENTILE'] = get_percentile('economic', summary[city]['economic_index'], economic_sort)
        dic['UNEMPLOYMENT_PERCENTILE'] = get_percentile('unemployment', summary[city]['unemployment_rate'],
                                                        unemployment_sort)
        dic['WORD_COUNT'] = summary[city]['word_count']
        dic['WORD_COUNT_PERCENTILE'] = get_percentile('word_count', summary[city]['word_count'], word_sort)
        dic['EMOTION_POSITIVE'] = summary[city]['emotion']['positive']
        dic['EMOTION_NEGATIVE'] = summary[city]['emotion']['negative']
        dic['EMOTION_NEUTRAL'] = summary[city]['emotion']['neutral']
        output.append(dic)
        count += 1
    return output


# output the distribution statistics for each scenario in dictionary
def output_stat():
    data = output_data()
    education_step = ['0.75-1.0', '0.65-0.74', '0.55-0.64', '0.45-0.54', '0.4-0.44', '0.35-0.39', '0-0.34']
    economic_step = ['1075+', '1050-1074', '1025-1049', '1000-1024', '975-999', '950-974', '950-']
    unemployment_step = ['8.0+', '7.0-7.9', '6.5-6.9', '6.0-6.4', '5.5-5.9', '5.0-5.4', '5.0-']
    wordcount_step = ['900+', '700-899', '500-699', '300-499', '200-299', '100-199', '100-']
    education_distribution = {step: 0 for step in education_step}
    economic_distribution = {step: 0 for step in economic_step}
    unemployment_distribution = {step: 0 for step in unemployment_step}
    wordcount_distribution = {step: 0 for step in wordcount_step}
    for city in data:
        education, economic, unemployment, wordcount = list(city.values())[1:5]
        if education == 0:
            pass
        elif 1.0 >= education >= 0.75:
            education_distribution['0.75-1.0'] += 1
        elif 0.75 > education >= 0.65:
            education_distribution['0.65-0.74'] += 1
        elif 0.65 > education >= 0.55:
            education_distribution['0.55-0.64'] += 1
        elif 0.55 > education >= 0.45:
            education_distribution['0.45-0.54'] += 1
        elif 0.45 > education >= 0.4:
            education_distribution['0.4-0.44'] += 1
        elif 0.4 > education >= 0.35:
            education_distribution['0.35-0.39'] += 1
        elif 0.35 > education > 0:
            education_distribution['0-0.34'] += 1
        if economic == 0:
            pass
        elif economic >= 1075:
            economic_distribution['1075+'] += 1
        elif 1075 > economic >= 1050:
            economic_distribution['1050-1074'] += 1
        elif 1050 > economic >= 1025:
            economic_distribution['1025-1049'] += 1
        elif 1025 > economic >= 1000:
            economic_distribution['1000-1024'] += 1
        elif 1000 > economic >= 975:
            economic_distribution['975-999'] += 1
        elif 975 > economic >= 950:
            economic_distribution['950-974'] += 1
        elif 950 > economic > 0:
            economic_distribution['950-'] += 1
        if unemployment == 0:
            pass
        elif unemployment >= 8.0:
            unemployment_distribution['8.0+'] += 1
        elif 8.0 > unemployment >= 7.0:
            unemployment_distribution['7.0-7.9'] += 1
        elif 7.0 > unemployment >= 6.5:
            unemployment_distribution['6.5-6.9'] += 1
        elif 6.5 > unemployment >= 6.0:
            unemployment_distribution['6.0-6.4'] += 1
        elif 6.0 > unemployment >= 5.5:
            unemployment_distribution['5.5-5.9'] += 1
        elif 5.5 > unemployment >= 5.0:
            unemployment_distribution['5.0-5.4'] += 1
        elif unemployment < 5.0:
            unemployment_distribution['5.0-'] += 1
        if wordcount == 0:
            pass
        elif wordcount >= 900:
            wordcount_distribution['900+'] += 1
        elif 900 > wordcount >= 700:
            wordcount_distribution['700-899'] += 1
        elif 700 > wordcount >= 500:
            wordcount_distribution['500-699'] += 1
        elif 500 > wordcount >= 300:
            wordcount_distribution['300-499'] += 1
        elif 300 > wordcount >= 200:
            wordcount_distribution['200-299'] += 1
        elif 200 > wordcount >= 100:
            wordcount_distribution['100-199'] += 1
        elif 100 > wordcount >= 0:
            wordcount_distribution['100-'] += 1
    output = [education_distribution, economic_distribution, unemployment_distribution, wordcount_distribution]
    return output
print(output_stat())

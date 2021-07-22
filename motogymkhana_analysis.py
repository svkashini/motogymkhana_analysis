import numpy as np
import datetime
import plotly.express as px
import pandas as pd
import streamlit as st
from streamlit.logger import DEFAULT_LOG_MESSAGE

st.title('MotoGymkhana Result Database')
st.text('出典: 二輪ジムカーナ主催者団体協議会（ＪＡＧＥ） http://jage.jpn.org/claro/index.html')
st.text('出典: KRiSP(二輪の安全運転練習会・オンロード) | キョウセイドライバーランド https://www.kotsu-daigaku.jp/krisp.html')
st.text('データは出典元HP記載のリザルトを加工し作成')

add_selectbox = st.sidebar.selectbox(
    '参照データを選択',
    ('関東: DUNLOP杯, JAGE杯 (2011〜)', '中部: KRiSP（2017〜）')
)

add_checkbox = st.sidebar.checkbox(
    'シーズン中の同一ライダーの重複を除く'
)

if add_selectbox == '関東: DUNLOP杯, JAGE杯 (2011〜)':
    #関東データに適用
    df = pd.read_csv('data.csv', index_col=0)
    df = df.replace({'NN':'N', 'NO':'N', 'NX':'N'})
    df['Season'] = df['Date'].apply(lambda x: int(x[:4]))
    df = pd.read_csv('data.csv', index_col=0)
    df = df.replace({'NN':'N', 'NO':'N', 'NX':'N'})
    df['Season'] = df['Date'].apply(lambda x: int(x[:4]))
else:
    df = pd.read_csv('data_krisp.csv', index_col=0)


add_slider = st.sidebar.slider(
    'シーズンを選択',
    value = df['Season'].max().item(),
    min_value = df['Season'].min().item(),
    max_value = df['Season'].max().item(),
    step = 1
)

color_class = {
    'A':'red',
    'B':'blue',
    'C1':'lightgreen',
    'C2':'limegreen',
    'N':'yellow',
    'NL':'pink',
    'C0':'green',
    'D1':'gray',
    'D2':'yellow',
    'D3':'orange'
    }

color_man = {
    'Honda':'red',
    'Suzuki':'yellow',
    'Kawasaki':'limegreen',
    'Yamaha':'blue',
    'KTM':'orange',
    'Ducati':'crimson'
    }

list_man = df['Manufacturer'].unique()

m_list2 = ['全メーカー'] + list_man.tolist()

option_man = st.sidebar.selectbox(
    'メーカーを選択',
    m_list2,
)

st.title('【シーズン別出走車両台数推移】')
st.text('注記）のべエントリー数で集計')

df_entry = df.groupby(['Season', 'Manufacturer'], as_index=False).count()
df_entry = df_entry[['Season','Manufacturer', 'Rider']]

fig = px.bar(
    data_frame = df_entry.sort_values('Rider', ascending=False),
    x = 'Season',
    y = 'Rider',
    color = 'Manufacturer',
    color_discrete_map = color_man,
    labels = {'Rider':'のべ出走台数（台）'},
)
st.plotly_chart(fig)

df_season = pd.crosstab(df.Season, df.Manufacturer, margins=True).sort_values(by='All', axis=1, ascending=False).iloc[:-1, 1:]
df_season


st.title('シーズン・車両別出走台数')

if add_checkbox == True:
    temp = pd.DataFrame()
    for year in df['Season'].unique():
        df_year = df[df['Season']==year].sort_values('Class')
        all_machine = df_year.drop_duplicates(subset=['Rider', 'Machine'])
        temp = pd.concat([temp, all_machine])
    df_m = temp
else:
    df_m = df

df_m = df_m.groupby(['Season', 'Machine', 'Manufacturer'], as_index=False).count()

if option_man != '全メーカー':
    df_m = df_m[df_m['Manufacturer']==option_man]

df_m = df_m[df_m['Season'] == add_slider]

disp_max = len(df_m['Machine'].unique())
disp_min = disp_max - 15.5

fig = px.bar(
    data_frame = df_m.sort_values(['Rider']),
    x = 'Rider',
    y = 'Machine',
    range_y = [disp_min, disp_max],
    title = add_selectbox[:2] + ': '+ str(add_slider) + '年の出走台数上位15車種 (' + str(option_man) + ')'
)
st.plotly_chart(fig)

show_detail = st.checkbox('16位以降を含めた全データの表を表示')
if show_detail == True:
    temp = df_m[['Manufacturer', 'Machine', 'Rider']].sort_values('Rider', ascending=False)
    temp

#車両別データの表示
st.title('【車両別データ】')

if option_man == '全メーカー':
    machine_list = ['全車種']
    df_machine = df
else:
    machine_list = df[df['Manufacturer']==option_man]['Machine'].unique()
    option_machine = st.sidebar.selectbox(
        '車両を選択',
        ['全車種'] + np.sort(machine_list).tolist(),
    )
if option_man != '全メーカー':
    if option_machine != '全車種':
        df_machine = df[df['Machine']==option_machine]
    else:
        df_machine = df[df['Manufacturer']==option_man]

if add_checkbox == True:
    temp = pd.DataFrame()
    for year in df_machine['Season'].unique():
        df_year = df_machine[df_machine['Season']==year].sort_values('Class')
        all_machine = df_year[~df_year['Rider'].duplicated()]
        temp = pd.concat([temp, all_machine])
    df_machine = temp

#df_machine

#出走台数推移
year_max = df['Season'].max() + 1
year_min = df['Season'].min() - 1

if option_man == '全メーカー':
    graph_title =  add_selectbox + ': 出走台数推移(' + str(option_man) + ')'
else:
    graph_title =  add_selectbox + ': 出走台数推移(' + str(option_man) +', ' + str(option_machine) + ')'

fig = px.bar(
    data_frame = df_machine.groupby(['Season', 'Class'], as_index=False).count()[['Season', 'Class', 'Rider']].sort_values('Class'),
    x = 'Season',
    y = 'Rider',
    range_x = [year_min, year_max],
    color = 'Class',
    color_discrete_map = color_class,
    labels = {'Rider':'出走台数（台）'},
    title = graph_title
)
st.plotly_chart(fig)




st.header('タイム比推移・分布')
class_list = ['全て'] + np.sort(df['Class'].unique()).tolist()
option_class = st.selectbox('クラスを選択', class_list)
if option_class == '全て':
    df_class = df
else:
    df_class = df[df['Class']==option_class]

if option_man != '全メーカー':
    if option_machine == '全車種':
        df_class = df_class[df_class['Manufacturer']==option_man]
        graph_title = add_selectbox + ', ' + option_man
    else:
        df_class = df_class[df_class['Machine']==option_machine]
        graph_title = add_selectbox + ', ' + option_man + ', ' + option_machine
else:
    graph_title = add_selectbox + ', ' + option_man

fig = px.scatter(
    data_frame = df_class.sort_values('Class'),
    x = 'Date',
    y = 'Rating[%]',
    color = 'Class',
    color_discrete_map = color_class,
    range_x = [datetime.datetime(year_min.item()+1,1,1), datetime.datetime(year_max.item(),1,1)],
    range_y = [160, 100],
    labels = {'Rating[%]':'タイム比[%]'},
    title = graph_title
)
st.plotly_chart(fig)




slider_range2 = st.slider(
    '期間を選択',
    value = [year_min.item()+1, year_max.item()-1],
    min_value = year_min.item()+1,
    max_value = year_max.item()-1,
    step = 1
    )

fig = px.histogram(
    data_frame = df_class[(df_class['Season']>=slider_range2[0]) & (df_class['Season']<=slider_range2[1])].sort_values('Class'),
    x = 'Rating[%]',
    color = 'Class',
    range_x = [100, 160],
    barmode = 'stack',
    color_discrete_map = color_class,
    title = graph_title + '(' + str(slider_range2[0]) + '〜' + str(slider_range2[1]) +')'
)

st.plotly_chart(fig)



if add_selectbox == '関東: DUNLOP杯, JAGE杯 (2011〜)':
    st.title('クラス昇格者の使用車両')
    classup_list = ['Bへ昇格', 'C1へ昇格', 'C2へ昇格']
    option_classup = st.selectbox('選択して下さい', classup_list)

    #B級昇格者の抽出
    to_b = df[df['Rating[%]'] < 105]
    to_b = to_b[(to_b['Class'] !='A') & (to_b['Class']!= 'B')]

    #C1級昇格者の抽出
    to_c1 = df[df['Rating[%]'] < 110]
    to_c1 = to_c1[(to_c1['Class'] !='A') & (to_c1['Class']!= 'B') & (to_c1['Class']!= 'C1')]

    #C2級昇格者の抽出
    to_c2 = df[df['Rating[%]'] < 115]
    to_c2 = to_c2[to_c2['Class'].str.contains('N')]

    if option_classup == 'Bへ昇格':
        df_classup = to_b
    elif option_classup == 'C1へ昇格':
        df_classup = to_c1
    else:
        df_classup = to_c2

    slider_range = st.slider(
        '抽出期間を選択',
        value = [2011, 2021],
        min_value = 2011,
        max_value = 2021,
        step = 1
        )

    df_classup = df_classup[(df_classup['Season']>=slider_range[0])&(df_classup['Season']<=slider_range[1])]
    temp = df_classup.groupby(['Machine', 'Manufacturer'], as_index=False).count()[['Machine','Rider', 'Manufacturer']].sort_values('Rider', ascending=False)
    df_classup = df_classup['Machine'].value_counts()

    fig = px.bar(
        df_classup.sort_values().reset_index().rename(columns={'index': 'Machine', 'Machine':'昇格者数（人）'}),
        x = '昇格者数（人）',
        y = 'Machine',
        orientation = 'h'
    )
    st.plotly_chart(fig)
    temp
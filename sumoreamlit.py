######################## 基本機能 ########################
import numpy as np
import pandas as pd
from PIL import Image
import math

####################### スプシ関連 #######################
import gspread
from google.oauth2.service_account import Credentials

################### 住所⇒緯度経度変換 ####################
import requests
# import urllib

##################### streamlit関連 #####################
import streamlit as st
import folium
from streamlit_folium import folium_static
import altair as alt

#################### matplotlib関連 #####################

# import matplotlib.pyplot as plt
# import japanize_matplotlib

###################### seaborn関連 ######################

# import seaborn as sns

###################### plotly関連 #######################

# import plotly.figure_factory as ff
# import plotly.graph_objects as go

################## streamlit ページ設定 ##################

st.set_page_config(layout="wide")


##################### スプシ初期設定 #####################

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = Credentials.from_service_account_file(
    'service_account.json',
    scopes=scopes
)

gc = gspread.authorize(credentials)

SP_SHEET_KEY = '1wuBRHEBUbd1bmGikcU0hEQ2F3k94fp69JFfpX1_SO_w'

sh = gc.open_by_key(SP_SHEET_KEY)

SP_SHEET_PRO = 'suumo_data_old'
worksheet = sh.worksheet(SP_SHEET_PRO)
data = worksheet.get_all_values()

SP_SHEET_ANY = 'anytimefitness'
worksheet_any = sh.worksheet(SP_SHEET_ANY)
data_any = worksheet_any.get_all_values()

SP_SHEET_SUP = 'supermarket'
worksheet_sup = sh.worksheet(SP_SHEET_SUP)
data_sup = worksheet_sup.get_all_values()

SP_SHEET_SEN = 'sento'
worksheet_sen = sh.worksheet(SP_SHEET_SEN)
data_sen = worksheet_sen.get_all_values()

SP_SHEET_STA = 'station'
worksheet_sta = sh.worksheet(SP_SHEET_STA)
data_sta = worksheet_sta.get_all_values()


#################### プレーン地図生成 ####################

map = folium.Map(
    # 初期位置
    location=[35.6088281, 139.7261472],

    # 初期zoom設定
    zoom_start = 13,

    # 地図のスタイル
    title = 'OpenStreetMpa'
    # title = 'cartodbpositron'
    # title = 'Stamen Toner'
    # title = 'Stamen Terrain'
)


#################### 緯度経度初期設定 ####################

# makeUrl = "https://msearch.gsi.go.jp/address-search/AddressSearch?q="



######################## アプリ化 ########################

phase = st.sidebar.radio(
    label='',
    options=('物件選定', 'LINEへの通知'),
    index=0,
    horizontal=True
)

if phase == '物件選定' :

    st.title('理想の暮らしを手に入れませんか？(首都圏編)')
    image=Image.open('QOL爆上がり.png')
    st.image(image, use_column_width = True)

    st.subheader('あなたの叶えたい暮らしから家を選ぼう')

    left_column, right_column = st.columns(2)

    with left_column:
        select_image1 = st.checkbox(label='ていねいな暮らし')
        image_oshare=Image.open('QOL爆上がり.png')
        st.image(image_oshare, use_column_width = True)
        select_image2 = st.checkbox(label='子育て向け')
        image_child=Image.open('子育て.png')
        st.image(image_child, use_column_width = True)
        
    with right_column:
        select_image3 = st.checkbox(label='カップル向け')
        image_couple=Image.open('カップル向け.png')
        st.image(image_couple, use_column_width = True)
        select_image4 = st.checkbox(label='ペットOK')
        image_pet=Image.open('ペットOK.png')
        st.image(image_pet, use_column_width = True)

    st.subheader('近くにあってほしい施設')
    select_ins1 = st.multiselect(label='500m以内にあってほしい施設を選んでください。', options=['スーパー', 'サウナ', 'ジム', '保育園', '銭湯'])
    select_ins2 = st.multiselect(label='1000m以内にあってほしい施設を選んでください。', options=['スーパー', 'サウナ', 'ジム', '保育園', '銭湯'])
    left_ins, center_ins, right_ins = st.columns(3)

    with left_ins:
        image_super=Image.open('スーパー.png')
        st.image(image_super, use_column_width = True)
        # st.write('スーパー')
        image_nursely=Image.open('保育園.png')
        st.image(image_nursely, use_column_width = True)
        # st.write('保育園')

    with center_ins:
        image_sauna=Image.open('サウナ.png')
        st.image(image_sauna, use_column_width = True)
        # st.write('サウナ')
        image_sentou=Image.open('銭湯.png')
        st.image(image_sentou, use_column_width = True)
        # st.write('銭湯')

    with right_ins:
        image_gym=Image.open('ジム.png')
        st.image(image_gym, use_column_width = True)
        # st.write('ジム')
        image_comin=Image.open('カミングスーン.png')
        st.image(image_comin, use_column_width = True)
        # st.write('')


    st.subheader('住みたい地域を選んで理想の物件を探そう')

    st.selectbox('都道府県の選択', ('東京都', '神奈川県', '千葉県', '埼玉県'))

    st.selectbox('区の選択', ('品川区', '港区', '世田谷区', '略'))


    ################ 絞り込み条件（初期値）################

    cost_min, cost_max = 0, 40
    area_min, area_max = 40, 90
    distance_min, distance_max = 0, 15
    age_min, age_max = 0, 30

    ####################### アプリ設定 #######################

    df = pd.DataFrame(data)
    df_any = pd.DataFrame(data_any)
    df_sup = pd.DataFrame(data_sup)
    df_sta = pd.DataFrame(data_sta)

    _df_rank = []
    _df_info = []

    r_any=500
    r_sup=1000
    r_sen=500
    r_sta=1000

    for i in range(6000, 8000, 10):

        ################### 条件に合う物件情報取得 ###################

        # 家賃+管理費の定義
        rent_df = float(df[8][i])
        mane_df = int(df[9][i])*0.0001
        mar_df = rent_df + mane_df

        # 月額費用、専有面積、駅までの距離、築年数による絞り込み反映
        if cost_min <= mar_df <= cost_max and area_min <= float(df[13][i]) <= area_max and distance_min <= int(df[19][i]) <= distance_max and age_min <= int(df[5][i]) <= age_max :
            
            # 条件に合う物件名を代入（マップのピンのポップアップに物件名を表示させるため、毎回データが変わる仕様に）
            property_name = df[0][i]
            
            ####################### 物件マップ #######################

            # 緯度経度取得
            lat_tude = df[30][i]
            lon_tude = df[29][i]
            
            for j in range(30, 80):

                anytime_name = df_any[1][j]

                lat_tude_any = float(df_any[11][j])
                lon_tude_any = float(df_any[10][j])

                dista_lat_any = (float(lat_tude) - float(lat_tude_any))*110.9463*1000
                dista_lon_any = (float(lon_tude) - float(lon_tude_any))*90.4219*1000
                distance_any = math.ceil((math.sqrt(dista_lat_any*dista_lat_any + dista_lon_any*dista_lon_any)))

                for k in range(2, 92):

                    super_name = df_sup[1][k]

                    lat_tude_sup = float(df_sup[8][k])
                    lon_tude_sup = float(df_sup[7][k])

                    dista_lat_sup = (float(lat_tude) - float(lat_tude_sup))*110.9463*1000
                    dista_lon_sup = (float(lon_tude) - float(lon_tude_sup))*90.4219*1000
                    distance_sup = math.ceil((math.sqrt(dista_lat_sup*dista_lat_sup + dista_lon_sup*dista_lon_sup)))


                    if distance_any <= r_any and distance_sup <= r_sup:
                    
                        folium.Marker(
                            location=[lat_tude_any, lon_tude_any],
                            icon=folium.Icon(color='purple', icon='user'),
                            popup=anytime_name
                        ).add_to(map)

                        folium.Marker(
                            location=[lat_tude_sup, lon_tude_sup],
                            icon=folium.Icon(color='blue', icon='bell'),
                            popup=super_name
                        ).add_to(map)

                        if mar_df >= 30 :
                            folium.Marker(
                                location=[lat_tude, lon_tude],
                                icon=folium.Icon(color='red', icon='home'),
                                popup=property_name
                            ).add_to(map)
                        elif 20 <= mar_df < 30 :
                            folium.Marker(
                                location=[lat_tude, lon_tude],
                                icon=folium.Icon(color='orange', icon='home'),
                                popup=property_name
                            ).add_to(map)
                        elif 10 <= mar_df < 20 :
                            folium.Marker(
                                location=[lat_tude, lon_tude],
                                icon=folium.Icon(color='green', icon='home'),
                                popup=property_name
                            ).add_to(map)
                        else :
                            folium.Marker(
                                location=[lat_tude, lon_tude],
                                icon=folium.Icon(color='blue', icon='home'),
                                popup=property_name
                            ).add_to(map)

                        folium.Circle(
                        radius=r_any,
                        location=[lat_tude, lon_tude],
                        # 外枠の色
                        color='purple',
                        # 円の塗りつぶし選択
                        fill = False,
                        # 塗りつぶす色の設定
                        # fill_color = 'lightgreen',
                        ).add_to(map)

                        folium.Circle(
                        radius=r_sup,
                        location=[lat_tude, lon_tude],
                        # 外枠の色
                        color='blue',
                        # 円の塗りつぶし選択
                        fill = False,
                        # 塗りつぶす色の設定
                        # fill_color = 'lightgreen',
                        ).add_to(map)
                

                        ############### 物件追加情報とポイント設定 ###############

                        name = df[0][i]
                        address = df[1][i]
                        access1 = df[2][i]
                        access2 = df[3][i]
                        access3 = df[4][i]

                        floor_plan = df[12][i]

                        deposit = df[10][i]
                        key_money = df[11][i]

                        room = int(df[24][i])
                        s = int(df[25][i])
                        l = int(df[26][i])
                        d = int(df[27][i])
                        k = int(df[28][i])

                        floor = int(df[7][i])
                        if floor >= 10 :
                            _floor = 2
                        elif 4 <= floor < 10 :
                            _floor = 1
                        elif 2 <= floor < 4 :
                            _floor = 1
                        else :
                            _floor = -1

                        evaluation = room + s + l + d + k + _floor

                        _df_info_ = [name, address, access1, access2, access3, floor, floor_plan, deposit, key_money]
                        _df_info.append(_df_info_)
                        df_info = pd.DataFrame(_df_info)
                        df_info.columns = ['物件名', '住所', 'アクセス1', 'アクセス2', 'アクセス3', '階数', '間取り', '敷金（万円）', '礼金（万円）']


                        ################ 評価ポイントのグラフ化 #################

                        _df_rank_ = [property_name, evaluation]
                        _df_rank.append(_df_rank_)
                        df_rank = pd.DataFrame(_df_rank)
                        df_rank.columns = ['物件名', '評価ポイント']

                        # chart = (
                        #         alt.Chart(df_rank)
                        #         .mark_bar(opacity=0.8, clip=True)
                        #         .encode(
                        #             x='物件名',
                        #             y='評価ポイント',
                        # #             color=alt.Color('usage_guide', scale=alt.Scale(domain=variable.usage_guide, range=["blue", "red"]))
                        #         )
                        #         .properties(
                        #             width=300, height=400
                        #         )
                        # )


#                         fig = plt.figure() 
#                         ax = fig.add_subplot()
#                         ax.bar(df_rank.index, df_rank['評価ポイント'])
#                         ax.set_ylim(0, 10, 1)
#                         # ax.set_yticks([0, 1, 2])
#                         ax.set_title('評価ポイント')
#                         ax.set_xlabel('物件名')
#                         ax.set_ylabel('ポイント')
#                         plt.tight_layout()

                        # sns.set(font="IPAexGothic")
                        # fig = sns.pairplot(df_rank)


                        # chart = go.Figure(
                        #         data = df_rank
                        # )

                        # chart = sns.barplot(data = df_rank,
                        #                     x='物件名',
                        #                     y='評価ポイント',
                        #                     # palette=sns.color_palette('dark:#5A9_r')
                        # )


            else :
                continue


    ####################### スーモ条件 #######################

    conditions = ['バス・トイレ別', '鉄筋・鉄骨', 'バルコニー・ルーフバルコニー付き', 'インターネット無料']
    df_con = pd.DataFrame(data=conditions)


    ######################## アプリ化 ########################

    if len(df_info) < 10 :

        st.write(f'現在の候補物件は{len(df_info)}件です。(同物件フロア違い含む)')

        button = st.button('マップで見る')

        if button :

            st.sidebar.subheader('以下の条件を変更できます')
            cost_min, cost_max = st.sidebar.slider('家賃+管理費（万円）',5, 50, (0, 40))
            area_min, area_max = st.sidebar.slider('専有面積（m2）',10, 90, (40, 90))
            distance_min, distance_max = st.sidebar.slider('駅までの距離（徒歩分）',0, 30, (0, 15))
            age_min, age_max = st.sidebar.slider('築年数（年）',0, 80, (0, 30))

            folium_static(map)

            # left_column, right_column = st.columns(2)

            # with left_column:
            #     st.subheader('物件詳細')
            #     st.write(df_info)
            #     st.subheader('評価項目')
            #     st.write('部屋数：部屋数分加点')
            #     st.write('SLDK：それぞれ1P')
            #     st.write('階層：10F以上2P, 4-9Fが1P, 2-3Fが0P, 1Fが-1P')
                
            # with right_column:
            #     st.subheader('評価ポイント')
            #     # st.altair_chart(chart, use_container_width=True)
            #     # st.plotly_chart(chart, use_container_width=True)
            #     st.pyplot(fig)

            st.write('本当はここに1アクションほしい')

            st.subheader('あなたにぴったりの家はこれだ！')
            st.write('物件詳細')
            st.write(df_info)
            st.write('スーモでの絞り込み条件')
            st.write(df_con)
            st.write('周辺施設充実度')
            image_report=Image.open('レーダーチャート.png')
            st.image(image_report)

            st.subheader('今回の条件を記録しておこう！')
            st.write('LINEにご登録いただくと、今回の条件をお送りすることができます')
            st.write('次回のお引越しの際にご活用ください')
            line_messa = st.button('今回の条件をLINEで通知する')


    elif len(df_info) == 0 :
        st.error('該当物件がありません')

    else :
        st.error(f'候補物件が多すぎます({len(df_info)}件)。もう少し絞り込んでみましょう！')


elif phase == 'LINEへの通知' :

    st.title('LINEへの通知完了メッセージ')
    st.write('LINEへ今回の条件を送信しました。')
    st.write('※LINE登録作業は省略')

    #必要な変数を設定
    #取得したトークン
    TOKEN = '92LIGkCfU9s0TQSX7Hr9iGEAxrBZOmDin9LMmr9HlDo'
    #APIのURL
    api_url = 'https://notify-api.line.me/api/notify'
    #送りたい内容
    send_contents = '前回の物件条件とスーモのリンクです。'
    send_suumo_link = 'https://suumo.jp/chintai/jnc_000080387285/?bc=100309713076'

    #情報を辞書型にする
    TOKEN_dic = {'Authorization': 'Bearer' + ' ' + TOKEN} 
    send_dic1 = {'message': send_contents}
    send_dic2 = {'message': send_suumo_link}

    #画像ファイルのパスを指定
    image_file = r'C:\Users\tatsu\再SUUMO発表デモ\前回の物件情報.png'

    #バイナリデータで読み込む
    binary = open(image_file, mode='rb')
    #指定の辞書型にする
    image_dic = {'imageFile': binary}

    #LINEに画像とメッセージを送る
    requests.post(api_url, headers=TOKEN_dic, data=send_dic1, files=image_dic)
    requests.post(api_url, headers=TOKEN_dic, data=send_dic2)

from database_management import create_local_db,create_tables,upload_existing_data
import sqlite3
import os
import streamlit as st

users_list=None
all_items=None
category_details=None
catg_details=None

conn = sqlite3.connect("shopping.db")
cursor = conn.cursor()
import time

def prepare_data():
    create_local_db()
    create_tables()
    upload_existing_data()

def get_llm():
    # !pip install -q together
    from dotenv import load_dotenv
    load_dotenv('.env')
    openai_endpoint = os.getenv("OPENAI_ENDPOINT")
    openai_apikey = os.getenv("OPENAI_APIKEY")
    deployment_name = os.getenv("DEPLOYMENT_NAME")
    from openai import AzureOpenAI
    client = AzureOpenAI(api_key = openai_apikey, azure_endpoint = openai_endpoint,api_version = "2024-05-01-preview")
    return client

def add_new_user(user_name:str,user_mail:str):
    query = """Insert into users (user_name,user_mail) 
    values (?,?)"""
    cursor.execute(query,(user_name,user_mail))
    conn.commit()
    print("user name added to db")
    cursor.execute("select user_name from users")
    global users_list
    users_list = cursor.fetchall()
    users_list = list(map(lambda x: x[0], users_list))

def recategorize_user(user_name:str,category:str):
    query = """update users
    set category_id =?
    where user_name = ?"""
    category_id = catg_details.get(category)
    cursor.execute(query,(category_id,user_name))
    conn.commit()
    # print("category id updated successfuly")

def get_user_shoppig_details(user_name:str):
    query = """select o.order_name,o.order_value,c.category_name from orders o
    join users u on u.user_id=o.user_id
    join categories c on c.category_id=u.category_id
    where u.user_name=?"""
    cursor.execute(query,(user_name,))
    out = cursor.fetchall()
    return out

def add_to_shoppping_history(user_name:str,item:str,cost:int):
    query = """insert into orders (user_id,order_name,order_value)
    select user_id,?,? from users 
    where users.user_name==?"""
    cursor.evaluate(query,(item,cost,user_name))
    conn.commit()

def auto_recommend_next_item(user_name,next_item,cost):
    historic_data = get_user_shoppig_details(user_name)
    system_prompt = f"""You're a recomendation agent for user in a shopping app. 
    Currently few users are categorized into multiple categories based on thier historic shopping activites on type of items they had purchased along with their purchasing capacities.
    
    Now you have to recategorize the user based on thier next purchase activites and then recommend them with next item they would be intrested in buying."""
    user_input=f"""
    CATEGORY DETAILS : {category_details}
    
    USER HISTORIC DATA: {historic_data}
    
    NEW ITEM: {next_item}
    COST: {cost}
    """
    output_format="""{
    "NEXT_RECOMENDATION":<>
    "CATEGORY":<>
    }"""
    user_instructions="Make sure to return output without additional explainations, next recomendation should be just the item/s, category should be one among the exisitng list"
    response = client.chat.completions.create(model = os.getenv("DEPLOYMENT_NAME"),
                               messages=[{"role":"system","content":system_prompt},
                                        {"role":"user","content":user_input},
                                        {"role":"user","content":user_instructions},
                                        {"role":"user","content":output_format}]
                              )
    out = response.choices[0].message.content
    import json
    out = json.loads(out)
    recategorize_user(user_name,out["CATEGORY"])
    return out

def main_setup():

    cursor.execute("select user_name from users")
    global users_list
    users_list = cursor.fetchall()
    users_list = list(map(lambda x: x[0], users_list))

    items_query = "select items from categories where items is not null"
    cursor.execute(items_query)
    global all_items
    all_items = cursor.fetchall()
    all_items = list(map(lambda x:x[0].split(', '), all_items))
    all_items = list({item for lst in all_items for item in lst})

    cursor.execute("select category_name,spend_capacity,items from categories")
    global category_details
    category_details = cursor.fetchall()

    cursor.execute("select category_name,category_id from categories")
    out = cursor.fetchall()
    global catg_details
    catg_details = {key:value for key,value in out}

client = get_llm()
main_setup()

st.title("E-shopping")
st.write("Welcome, have a good shopping !!")

user_valid = False

if user_name := st.text_input(label="Please identify your self with your name"):
    if user_name not in users_list:
        st.markdown("We see new to join, please sign up below.")
        user_mail = st.text_input(label="Please provide your mail-id")
        add_new_user(user_name,user_mail)
        st.markdown("you're set to shop now")
        user_valid = True
    else:
        user_valid = True

if user_valid:
    continue_shopping = "Continue"
    index = 0
    st.session_state.recomendation = ''
    st.session_state.iscontinue = True
    if st.session_state.iscontinue:
        with st.form(f"item_details_{index}") as form:
            if st.session_state.recomendation != '':
                item_name = st.text_input(label="Item you want to buy", value=st.session_state.recomendation)
            else:
                item_name = st.text_input(label="Item you want to buy")
            cost = st.number_input("Item cost")
            submit = st.form_submit_button("Submit")

            if submit:
                recomendation = auto_recommend_next_item(user_name,item_name,cost)
                st.markdown(f"We have a new recommendation to you, intrested in buying more of this??? \n*********{recomendation["NEXT_RECOMENDATION"]}********* ")   
                st.session_state.recomendation = recomendation["NEXT_RECOMENDATION"]
                index +=1
                continue_shopping = st.radio("Do you want to continue shopping?", options=[True, False])
    else:
        st.markdown("Got it, you want to end now!!")

        








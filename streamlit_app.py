# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

st.title("Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie.")

name_on_order = st.text_input('Name On Smoothie')
st.write('The name on your Smoothie will be:', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

# Include both columns in the query
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('fruit_name'), col('search_on')
)
pd_df = my_dataframe.to_pandas()

# After converting to pandas, normalize column names
pd_df.columns = pd_df.columns.str.lower()

# Use lowercase column names
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['fruit_name'].tolist(),
    max_selections=5
)


if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)
    
    for fruit_chosen in ingredients_list:
        filtered = pd_df.loc[pd_df['fruit_name'] == fruit_chosen]
        if not filtered.empty:
            search_on = filtered['search_on'].iloc[0]
            st.subheader(f"{fruit_chosen} Nutrition Information")
            response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
            st.dataframe(data=response.json(), use_container_width=True)
        else:
            st.warning(f"No data found for {fruit_chosen}")
    
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """
    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")

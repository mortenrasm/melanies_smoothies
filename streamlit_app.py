# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas 

# Write directly to the app
st.title("Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie.")

name_on_order = st.text_input('Name On Smoothie')
st.write('The name on your Smoothie will be:', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

# Select both 'fruit_name' and 'search_on' columns
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('fruit_name'), col('search_on')
)
pd_df = my_dataframe.to_pandas()

# Use pandas column for options in multiselect
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['fruit_name'].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    for fruit_chosen in ingredients_list:
        # Defensive: check if the fruit exists in the DataFrame
        filtered = pd_df.loc[pd_df['fruit_name'] == fruit_chosen]
        if not filtered.empty:
            search_on = filtered['search_on'].iloc[0]
            st.subheader(f"{fruit_chosen} Nutrition Information")
            smoothiefroot_response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{search_on}"
            )
            st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        else:
            st.warning(f"No search value found for {fruit_chosen}")

    my_insert_stmt = f"""
        insert into smoothies.public.orders(ingredients, name_on_order)
        values ('{ingredients_string}', '{name_on_order}')
    """
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")

# Example display for a default fruit
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

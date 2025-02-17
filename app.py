import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_shopify_partners(page_number):
    url = f"https://www.shopify.com/partners/directory/services?page={page_number}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    partner_cards = soup.find_all('div', {'data-component-name': 'listing-profile-card'})

    partners_data = []

    for card in partner_cards:
        partner_name = card.find('h3', class_='md:mb-1 text-xl font-semibold text-gray-900 xs:mb-0').text.strip()
        location = card.find('span', class_='text-gray-500 text-base').text.strip()
        rating = card.find('span', class_='pl-1 text-base').text.strip()
        
        profile_link = card.find('a', class_='w-full pt-4 pr-6 pb-4 pl-4 bg-transparent grid xs:grid-cols-[80px_1fr] md:grid-cols-[91px_1fr] grid-rows-[auto_auto]')['href']
        full_profile_url = f"https://www.shopify.com{profile_link}"
        
        profile_response = requests.get(full_profile_url, headers=headers)
        profile_soup = BeautifulSoup(profile_response.text, 'html.parser')
        
        profile_section = profile_soup.find('section', {'data-component-name': 'profile'})
        
        email = phone_number = website = facebook = linkedin = instagram = twitter = None
        
        contact_links = profile_section.find_all('a', class_="hover:underline focus:underline")
        social_media_links = profile_section.find_all('a', target="_blank", rel="noreferrer")
        
        for link in contact_links:
            href = link.get('href')
            if href.startswith("mailto:"):
                email = href.replace("mailto:", "").strip()
            elif href.startswith("tel:"):
                phone_number = href.replace("tel:", "").strip()
            elif href.startswith("https://"):
                website = href.strip()

        for link in social_media_links:
            href = link.get('href')
            if href.startswith("https://www.facebook.com/"):
                facebook = href.strip()
            elif href.startswith("https://www.linkedin.com/"):
                linkedin = href.strip()
            elif href.startswith("https://www.instagram.com/"):
                instagram = href.strip()
            elif href.startswith("https://x.com/"):
                twitter = href.strip()
        
        partners_data.append({
            'Name': partner_name,
            'Location': location,
            'Rating': rating,
            'Email': email if email else "N/A",
            'Phone Number': phone_number if phone_number else "N/A",
            'Profile URL': full_profile_url,
            'Website': website if website else "N/A",
            'Facebook': facebook if facebook else "N/A",
            'LinkedIn': linkedin if linkedin else "N/A",
            'Instagram': instagram if instagram else "N/A",
            'Twitter': twitter if twitter else "N/A"
        })
        
        time.sleep(1)

    return pd.DataFrame(partners_data)

st.title("Shopify Partners Directory Scraper")

page_number = st.number_input("Enter page number to scrape", min_value=1, value=1, step=1)

if st.button("Scrape Data"):
    with st.spinner("Scraping data... This may take a few minutes."):
        df = scrape_shopify_partners(page_number)
    
    st.success("Data scraped successfully!")
    
    st.subheader("Scraped Data")
    st.dataframe(df)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"shopify_partners_page_{page_number}.csv",
        mime="text/csv"
    )

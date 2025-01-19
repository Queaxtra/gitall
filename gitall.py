import streamlit as st
import requests
from bs4 import BeautifulSoup
import json

st.set_page_config(
    page_title="GitHub Profile Viewer",
    layout="wide"
)

st.title("GitHub Profile Viewer")
st.subheader("Enter a GitHub username to view their profile")
st.markdown("---")

username = st.text_input("Enter GitHub Username", placeholder="e.g., Queaxtra", help="Enter the GitHub username of the user you want to view")

if username:
    if not username.isalnum():
        st.error("Please enter a valid GitHub username. Username should be alphanumeric.")
    else:
        with st.spinner('Loading data...'):
            base_url = f'https://github.com/{username}'
            all_repos = []

            page_number = 1
            while True:
                repos_url = f'{base_url}?tab=repositories&page={page_number}'
                repos_response = requests.get(repos_url)

                if repos_response.status_code != 200:
                    break 

                repos_soup = BeautifulSoup(repos_response.text, 'html.parser')
                repos = repos_soup.find_all('li', class_='col-12 d-flex flex-justify-between width-full py-4 border-bottom color-border-muted public source')

                if not repos:
                    break

                for repo in repos:
                    repo_name = repo.find('a', itemprop='name codeRepository')
                    repo_desc = repo.find('p', class_='col-9 d-inline-block color-fg-muted mb-2 pr-4')
                    repo_lang = repo.find('span', itemprop='programmingLanguage')
                    repo_stars = repo.find('a', class_='Link--muted mr-3')
                    
                    repo_data = {
                        'name': repo_name.text.strip() if repo_name else 'Unknown Repository',
                        'description': repo_desc.text.strip() if repo_desc else None,
                        'language': repo_lang.text.strip() if repo_lang else None,
                        'stars': repo_stars.text.strip() if repo_stars else '0',
                        'link': f'https://github.com/{username}/{repo_name.text.strip()}' if repo_name else None
                    }
                    all_repos.append(repo_data)

                page_number += 1

        profile_response = requests.get(base_url)
        if profile_response.status_code == 200:
            profile_soup = BeautifulSoup(profile_response.text, 'html.parser')

            if profile_response.status_code == 200:
                profile_soup = BeautifulSoup(profile_response.text, 'html.parser')


                st.header("User Information")
                
                avatar = profile_soup.find('img', class_='avatar avatar-user width-full border color-bg-default')
                if avatar:
                    st.image(avatar['src'], width=200)

                user_username = profile_soup.find('span', class_='p-nickname vcard-username d-block')
                name = profile_soup.find('span', class_='p-name vcard-fullname d-block overflow-hidden')
                bio = profile_soup.find('div', class_='p-note user-profile-bio mb-3 js-user-profile-bio f4')
                label = profile_soup.find('span', class_='Label Label--purple text-uppercase')
                org_span = profile_soup.find('span', class_='p-org')
                country_span = profile_soup.find('span', class_='p-label')
                org_div = profile_soup.find('div', class_='border-top color-border-muted pt-3 mt-3 clearfix hide-sm hide-md')
                additional_info_div = profile_soup.find('div', class_='flex-order-1 flex-md-order-none mt-2 mt-md-0')

                user_data = {
                    'username': user_username.text.strip() if user_username else None,
                    'name': name.text.strip() if name else None,
                    'bio': bio.text.strip() if bio else None,
                    'account_type': label.text.strip() if label else None,
                    'organization': org_span.text.strip() if org_span else None,
                    'country': country_span.text.strip() if country_span else None,
                    'avatar_url': avatar['src'] if avatar else None,
                    'repositories': all_repos
                }

                col1, col2 = st.columns(2)

                with col1:
                    if user_username:
                        st.info(f"**Username:** {user_data['username']}")
                    if name:
                        st.success(f"**Name:** {user_data['name']}")
                    if bio:
                        st.warning(f"**Bio:** {user_data['bio']}")
                    if additional_info_div:
                        followers_following = additional_info_div.text.strip().split('·')
                        followers = followers_following[0].strip()
                        st.info(f"**Followers:** {followers}")

                with col2:
                    if label:
                        st.warning(f"**Account Type:** {user_data['account_type']}")
                    if org_span:
                        st.info(f"**Organization:** {user_data['organization']}")
                    if country_span:
                        st.success(f"**Country:** {user_data['country']}")
                    if additional_info_div:
                        following = followers_following[1].strip()
                        st.warning(f"**Following:** {following}")

                if org_div:
                    st.header("Organization Information")
                    org_links = org_div.find_all('a')
                    for org_link in org_links:
                        org_label = org_link.get('aria-label')
                        if org_label:
                            st.info(f"**Organization:** {org_label}")

                st.header("Repository Information")
                
                if all_repos:
                    st.success(f"**Total Repository Count:** {len(all_repos)}")
                    
                    for repo in all_repos:
                        with st.expander(repo['name']):
                            if repo['description']:
                                st.markdown(f"**Description:** {repo['description']}")
                            if repo['language']:
                                st.info(f"**Programming Language:** {repo['language']}")
                            if repo['stars']:
                                stars = repo['stars']
                                st.warning(f"**Star Count:** {stars}")
                            if repo['link']:
                                st.markdown(f"[Go to Repository]({repo['link']})")

                else:
                    st.error("Repository not found or all are private.")

                st.header("User Data with JSON")
                st.json(user_data)

                if st.button("Click to compile user information."):
                    user_data_json = json.dumps(user_data, ensure_ascii=False, indent=4)
                    st.download_button(
                        label="Download User Data",
                        data=user_data_json,
                        file_name=f"{user_data['username']}_data.json",
                        mime="application/json"
                    )

            else:
                st.error(f"Data fetching error! Profile: {profile_response.status_code}")

st.markdown("---")
st.markdown("Made with ❤️ by Quaxtra")
st.markdown("This project is open sourced on [GitHub](https://github.com/Queaxtra/gitall)")
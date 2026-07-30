<!-- Coding from scratch -->

# 1. Connect gitHub with the Backend 
### 2 ways to do 
1. Github REST API
2. PyGithub -> automated Python library 


#### For now I will be using a PAT(Personal Access token) -> fine Grained for access to a specific repo 
##### When we move to development phase later : 
1. Create Another fine grained token and give access to other repos 
2. Or give access to multiple repos on the same token 

##### In case of Production Phase 
1. This is going to be a Extension so, I will replace PAT auth entirely with GITHUB APP 
2. Users install the app on whichever repositories they want SpriteSRE to manage.

# 2. Once connected, I need to write fetch methods in github/client.py
- I will need Github API URL, PAT, headers and client again and again so -> therefore making a constructor 
- from the current fetched response I have a lot of fields but I only need 

##### Fields I am keeping in my schema of repository.py 
- Repository
- Owner
- Default Branch
- Visibility
- Clone URL
- Language
- Private 
- Updated at and Pushed at 
(because later SpriteSRE may display repository health.)
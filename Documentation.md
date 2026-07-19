<!-- Coding from scratch -->

# 1. Connect gitHub with the Backend 
-- 2 ways to do 
1. Github REST API
2. PyGithub -> automated Python library 


For now I will be using a PAT(Personal Access token) -> fine Grained for access to a specific repo 
When we move to development phase later : 
1. Create Another fine grained token and give access to other repos 
2. Or give access to multiple repos on the same token 

In case of Production Phase 
1. This is going to be a Extension so, I will replace PAT auth entirely with GITHUB APP 
2. Users install the app on whichever repositories they want SpriteSRE to manage.
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

### Made the GithubClient sdk
that has 
- __map_repository() -> private method
- __map_repository_file() -> private method
- __map_workflow() -> private method
- __request() -> private method
- get_repository() -> public method for endpoint
- get_contents() -> public method for endpoint
- get_workflows() -> public method for endpoint
- get_logs() -> public method for endpoint

##### But rn we ar polling -> making requests for every single thing, so without webhooks it's like I ask my friend every minute 
```
"Did the CI fail?"

"No."

"Did the CI fail?"

"No."

"Did the CI fail?"

"No."
```

This is called Polling.
It's wasteful.

### WITH WEBHOOKS 
Your friend says :
    "Don't keep asking me. If something happens, I'll call you."

```
GitHub
   │
Something happens
   │
   ▼
POST Request
   │
   ▼
SpriteSRE
```
No polling.
GitHub pushes the event.


### Phase 2 Architechture 
Github -> Workflow fails -> Github webhooks -> 200 POST/webhooks/github -> verify Sign -> Parse Payload -> create Incident -> Store In memory -> Return 200 OK 

### What actually happens but ?
When a worflow fails, Github sends an HTTP request. 

Literally, 
```
POST /webhooks/github  
```

Body: 
``` 
{
  "action":"completed",
  "workflow_run":{
      ...
  }
}
```
### But how do we know someone else didn't send it ?
#### because if I know anyones url I can send them anything, suppose I send this 
``` 
{
   "workflow_run":{
      "conclusion":"failure"
   }
}
```
Now SpriteSRE thinks my CI failed, but in actual it didn't. 


### Github solves this using HMAC (Hashing Technique)
So here, Github computes -> Payload + Secret -> SHA256 HMC -> Signature. 

Then it returns -> Payload + Signature (recieved by backend)
It recomputes -> payload + Same Secret -> SHA256 HMAC 

If MY sign == Github sign then payload authentic otherwise 403 forbidden 

So NOW the architechture becomes -> 
``` 

                GitHub
                   │
                   ▼
      POST /webhooks/github
                   │
                   ▼
      Signature Verification
                   │
         Valid? ───┴──── Invalid
           │                │
           ▼                ▼
     Parse Payload       403 Forbidden
           │
           ▼
    Create Incident

```
